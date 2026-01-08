import os
import smtplib
from email.mime.text import MIMEText
from typing import Literal

import httpx


def format_html_email(title: str, content: str, execution_time: str) -> str:
	"""将纯文本内容格式化为现代化的HTML邮件"""
	# 解析内容
	lines = content.split('\n')

	# 提取时间信息
	time_str = execution_time

	# 解析账号信息
	accounts = []
	stats = []

	current_section = None
	for line in lines:
		line = line.strip()
		if not line:
			continue

		# 跳过统计信息行
		if line.startswith('[STATS]') or line.startswith('[TIME]'):
			if line.startswith('[TIME]'):
				time_str = line.replace('[TIME] Execution time:', '').strip()
			continue

		# 统计信息行（包含 Success/Failed/All accounts 等关键词）
		if any(keyword in line for keyword in ['Success:', 'Failed:', 'All accounts', 'Some accounts']):
			stats.append(line)
			continue

		# 账号信息行
		if line.startswith('[BALANCE]'):
			# 余额信息
			name = line.replace('[BALANCE]', '').strip()
			current_section = {'type': 'balance', 'name': name, 'balance': '', 'status': 'success'}
			accounts.append(current_section)
		elif line.startswith('[SUCCESS]'):
			# 成功状态 - 只处理具体的账号行，跳过摘要行
			if 'Account' in line or not any(
				word in line for word in ['All accounts', 'Some accounts', 'check-in successful', 'check-in failed']
			):
				name = line.replace('[SUCCESS]', '').strip()
				current_section = {'type': 'success', 'name': name, 'status': 'success'}
				accounts.append(current_section)
		elif line.startswith('[FAIL]'):
			# 失败状态
			name = line.replace('[FAIL]', '').strip()
			current_section = {'type': 'fail', 'name': name, 'status': 'error'}
			accounts.append(current_section)
		elif line.startswith(':money:'):
			# 余额详情
			balance_info = line.replace(':money:', '').replace('Current balance:', '').strip()
			if current_section:
				current_section['balance'] = balance_info

	# 生成状态颜色和图标
	def get_status_color(status: str) -> str:
		if status == 'success':
			return '#10b981'
		elif status == 'error':
			return '#ef4444'
		return '#6b7280'

	def get_status_bg(status: str) -> str:
		if status == 'success':
			return '#d1fae5'
		elif status == 'error':
			return '#fee2e2'
		return '#f3f4f6'

	# 构建账号卡片
	account_cards = ''
	for acc in accounts:
		status_color = get_status_color(acc['status'])
		status_bg = get_status_bg(acc['status'])
		status_icon = '✓' if acc['status'] == 'success' else '✗'
		status_text = '签到成功' if acc['status'] == 'success' else '签到失败'

		card = f"""
		<div class="account-card">
			<div class="account-header">
				<span class="account-name">{acc['name']}</span>
				<span class="status-badge" style="background-color: {status_bg}; color: {status_color};">
					{status_icon} {status_text}
				</span>
			</div>
			{'<div class="balance-info">💰 ' + acc['balance'] + '</div>' if acc.get('balance') else ''}
		</div>"""
		account_cards += card

	# 解析统计信息
	success_count = 0
	fail_count = 0
	total_count = 0
	for stat in stats:
		if 'Success:' in stat:
			# 提取数字，格式: [SUCCESS] Success: 2/3
			parts = stat.split('Success:')[1].strip().split('/')
			success_count = int(parts[0])
			total_count = int(parts[1])
		elif 'Failed:' in stat:
			parts = stat.split('Failed:')[1].strip().split('/')
			fail_count = int(parts[0])

	# 构建HTML
	html = f"""
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<style>
		* {{ margin: 0; padding: 0; box-sizing: border-box; }}
		body {{
			font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
			background-color: #f5f7fa;
			padding: 20px;
			line-height: 1.6;
		}}
		.email-container {{
			max-width: 600px;
			margin: 0 auto;
			background-color: #ffffff;
			border-radius: 12px;
			overflow: hidden;
			box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
		}}
		.email-header {{
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
			color: white;
			padding: 30px;
			text-align: center;
		}}
		.email-header h1 {{
			font-size: 24px;
			font-weight: 600;
			margin-bottom: 8px;
		}}
		.email-header p {{
			font-size: 14px;
			opacity: 0.9;
		}}
		.email-content {{
			padding: 24px;
		}}
		.account-card {{
			background-color: #fafafa;
			border: 1px solid #e5e7eb;
			border-radius: 8px;
			padding: 16px;
			margin-bottom: 12px;
			transition: box-shadow 0.2s;
		}}
		.account-card:hover {{
			box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
		}}
		.account-header {{
			display: flex;
			justify-content: space-between;
			align-items: center;
			margin-bottom: 8px;
		}}
		.account-name {{
			font-size: 16px;
			font-weight: 600;
			color: #1f2937;
		}}
		.status-badge {{
			display: inline-block;
			padding: 4px 12px;
			border-radius: 20px;
			font-size: 12px;
			font-weight: 600;
		}}
		.balance-info {{
			font-size: 14px;
			color: #6b7280;
			margin-top: 4px;
		}}
		.stats-section {{
			background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
			border-radius: 8px;
			padding: 20px;
			margin-top: 20px;
			color: white;
		}}
		.stats-grid {{
			display: grid;
			grid-template-columns: repeat(3, 1fr);
			gap: 16px;
			text-align: center;
		}}
		.stat-item {{
			background-color: rgba(255, 255, 255, 0.2);
			border-radius: 8px;
			padding: 12px;
		}}
		.stat-label {{
			font-size: 12px;
			opacity: 0.9;
			margin-bottom: 4px;
		}}
		.stat-value {{
			font-size: 24px;
			font-weight: 700;
		}}
		.email-footer {{
			background-color: #f9fafb;
			padding: 20px;
			text-align: center;
			font-size: 12px;
			color: #9ca3af;
			border-top: 1px solid #e5e7eb;
		}}
	</style>
</head>
<body>
	<div class="email-container">
		<div class="email-header">
			<h1>{title}</h1>
			<p>{time_str}</p>
		</div>

		<div class="email-content">
			{account_cards if account_cards else '<p style="text-align: center; color: #9ca3af; padding: 20px;">暂无账号信息</p>'}

			<div class="stats-section">
				<div class="stats-grid">
					<div class="stat-item">
						<div class="stat-label">总计</div>
						<div class="stat-value">{total_count}</div>
					</div>
					<div class="stat-item">
						<div class="stat-label">成功</div>
						<div class="stat-value">{success_count}</div>
					</div>
					<div class="stat-item">
						<div class="stat-label">失败</div>
						<div class="stat-value">{fail_count}</div>
					</div>
				</div>
			</div>
		</div>

		<div class="email-footer">
			<p>此邮件由 AnyRouter 自动签到系统发送</p>
			<p style="margin-top: 4px;">Powered by Claude Code & GitHub Actions</p>
		</div>
	</div>
</body>
</html>"""
	return html


class NotificationKit:
	def __init__(self):
		self.email_user: str = os.getenv('EMAIL_USER', '')
		self.email_pass: str = os.getenv('EMAIL_PASS', '')
		self.email_to: str = os.getenv('EMAIL_TO', '')
		self.email_sender: str = os.getenv('EMAIL_SENDER', '')
		self.smtp_server: str = os.getenv('CUSTOM_SMTP_SERVER', '')
		self.pushplus_token = os.getenv('PUSHPLUS_TOKEN')
		self.server_push_key = os.getenv('SERVERPUSHKEY')
		self.dingding_webhook = os.getenv('DINGDING_WEBHOOK')
		self.feishu_webhook = os.getenv('FEISHU_WEBHOOK')
		self.weixin_webhook = os.getenv('WEIXIN_WEBHOOK')
		self.gotify_url = os.getenv('GOTIFY_URL')
		self.gotify_token = os.getenv('GOTIFY_TOKEN')
		gotify_priority_env = os.getenv('GOTIFY_PRIORITY', '9')
		self.gotify_priority = int(gotify_priority_env) if gotify_priority_env.strip() else 9
		self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
		self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

	def send_email(self, title: str, content: str, msg_type: Literal['text', 'html'] = 'text'):
		if not self.email_user or not self.email_pass or not self.email_to:
			raise ValueError('Email configuration not set')

		# 如果未设置 EMAIL_SENDER，使用 EMAIL_USER 作为默认值
		sender = self.email_sender if self.email_sender else self.email_user

		# MIMEText 需要 'plain' 或 'html'，而不是 'text'
		mime_subtype = 'plain' if msg_type == 'text' else 'html'
		msg = MIMEText(content, mime_subtype, 'utf-8')
		msg['From'] = f'AnyRouter Assistant <{sender}>'
		msg['To'] = self.email_to
		msg['Subject'] = title

		smtp_server = self.smtp_server if self.smtp_server else f'smtp.{self.email_user.split("@")[1]}'

		# 尝试多种连接方式
		last_error = None
		for method, port, use_ssl in [('SMTP_SSL', 465, True), ('STARTTLS', 587, False)]:
			try:
				if use_ssl:
					server = smtplib.SMTP_SSL(smtp_server, port, timeout=30)
				else:
					server = smtplib.SMTP(smtp_server, port, timeout=30)
					server.starttls()

				server.login(self.email_user, self.email_pass)
				server.send_message(msg)
				server.quit()
				return  # 发送成功，直接返回
			except Exception as e:
				last_error = e
				continue

		# 如果所有方法都失败，抛出最后一个错误
		raise last_error

	def send_pushplus(self, title: str, content: str):
		if not self.pushplus_token:
			raise ValueError('PushPlus Token not configured')

		data = {'token': self.pushplus_token, 'title': title, 'content': content, 'template': 'html'}
		with httpx.Client(timeout=30.0) as client:
			client.post('http://www.pushplus.plus/send', json=data)

	def send_serverPush(self, title: str, content: str):
		if not self.server_push_key:
			raise ValueError('Server Push key not configured')

		data = {'title': title, 'desp': content}
		with httpx.Client(timeout=30.0) as client:
			client.post(f'https://sctapi.ftqq.com/{self.server_push_key}.send', json=data)

	def send_dingtalk(self, title: str, content: str):
		if not self.dingding_webhook:
			raise ValueError('DingTalk Webhook not configured')

		data = {'msgtype': 'text', 'text': {'content': f'{title}\n{content}'}}
		with httpx.Client(timeout=30.0) as client:
			client.post(self.dingding_webhook, json=data)

	def send_feishu(self, title: str, content: str):
		if not self.feishu_webhook:
			raise ValueError('Feishu Webhook not configured')

		data = {
			'msg_type': 'interactive',
			'card': {
				'elements': [{'tag': 'markdown', 'content': content, 'text_align': 'left'}],
				'header': {'template': 'blue', 'title': {'content': title, 'tag': 'plain_text'}},
			},
		}
		with httpx.Client(timeout=30.0) as client:
			client.post(self.feishu_webhook, json=data)

	def send_wecom(self, title: str, content: str):
		if not self.weixin_webhook:
			raise ValueError('WeChat Work Webhook not configured')

		data = {'msgtype': 'text', 'text': {'content': f'{title}\n{content}'}}
		with httpx.Client(timeout=30.0) as client:
			client.post(self.weixin_webhook, json=data)

	def send_gotify(self, title: str, content: str):
		if not self.gotify_url or not self.gotify_token:
			raise ValueError('Gotify URL or Token not configured')

		# 使用环境变量配置的优先级，默认为9
		priority = self.gotify_priority

		# 确保优先级在有效范围内 (1-10)
		priority = max(1, min(10, priority))

		data = {'title': title, 'message': content, 'priority': priority}

		url = f'{self.gotify_url}?token={self.gotify_token}'
		with httpx.Client(timeout=30.0) as client:
			client.post(url, json=data)

	def send_telegram(self, title: str, content: str):
		if not self.telegram_bot_token or not self.telegram_chat_id:
			raise ValueError('Telegram Bot Token or Chat ID not configured')

		message = f'<b>{title}</b>\n\n{content}'
		data = {'chat_id': self.telegram_chat_id, 'text': message, 'parse_mode': 'HTML'}
		url = f'https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage'
		with httpx.Client(timeout=30.0) as client:
			client.post(url, json=data)

	def push_message(
		self, title: str, content: str, msg_type: Literal['text', 'html'] = 'text', execution_time: str = ''
	):
		notifications = []

		# 邮件使用 HTML 格式
		if execution_time:
			html_content = format_html_email(title, content, execution_time)
			notifications.append(('Email', lambda: self.send_email(title, html_content, 'html')))
		else:
			notifications.append(('Email', lambda: self.send_email(title, content, msg_type)))

		# 其他通知平台使用纯文本
		notifications.extend(
			[
				('PushPlus', lambda: self.send_pushplus(title, content)),
				('Server Push', lambda: self.send_serverPush(title, content)),
				('DingTalk', lambda: self.send_dingtalk(title, content)),
				('Feishu', lambda: self.send_feishu(title, content)),
				('WeChat Work', lambda: self.send_wecom(title, content)),
				('Gotify', lambda: self.send_gotify(title, content)),
				('Telegram', lambda: self.send_telegram(title, content)),
			]
		)

		for name, func in notifications:
			try:
				func()
				print(f'[{name}]: Message push successful!')
			except Exception as e:
				print(f'[{name}]: Message push failed! Reason: {str(e)}')


notify = NotificationKit()
