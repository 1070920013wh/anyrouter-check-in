#!/usr/bin/env python3
"""
邮件发送测试脚本
用于测试邮件通知功能是否正常工作
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 PATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from utils.notify import NotificationKit

load_dotenv(project_root / '.env')


def test_email_only():
	"""仅测试邮件发送"""
	print('[TEST] 开始测试邮件发送功能...\n')

	# 检查环境变量配置
	email_user = os.getenv('EMAIL_USER')
	email_pass = os.getenv('EMAIL_PASS')
	email_to = os.getenv('EMAIL_TO')

	if not email_user or not email_pass or not email_to:
		print('[ERROR] 邮件配置不完整，请检查以下环境变量：')
		print('  - EMAIL_USER: 发件人邮箱地址')
		print('  - EMAIL_PASS: 发件人邮箱密码/授权码')
		print('  - EMAIL_TO: 收件人邮箱地址')
		return False

	print(f'[CONFIG] 发件人: {email_user}')
	print(f'[CONFIG] 收件人: {email_to}')

	# 构建测试内容
	test_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	test_title = 'AnyRouter 签到测试邮件'
	test_content = f"""[TIME] Execution time: {test_time}

[BALANCE] 测试账号1
:money: Current balance: $25.00, Used: $5.00

[BALANCE] 测试账号2
:money: Current balance: $100.00, Used: $20.00

[STATS] Check-in result statistics:
[SUCCESS] Success: 2/2
[FAIL] Failed: 0/2
[SUCCESS] All accounts check-in successful!"""

	print('\n[CONTENT] 准备发送测试邮件...')
	print(f'[CONTENT] 标题: {test_title}')
	print(f'[CONTENT] 时间: {test_time}')

	# 发送邮件
	kit = NotificationKit()
	try:
		print('\n[SENDING] 正在发送邮件...')
		kit.send_email(test_title, test_content, msg_type='text')
		print('[SUCCESS] 邮件发送成功！')
		print(f'\n[INFO] 请检查收件箱 ({email_to}) 查看测试邮件')
		return True
	except Exception as e:
		print(f'[ERROR] 邮件发送失败: {e}')
		return False


def test_html_email():
	"""测试 HTML 格式邮件发送"""
	print('[TEST] 开始测试 HTML 邮件发送功能...\n')

	# 检查环境变量配置
	email_user = os.getenv('EMAIL_USER')
	email_pass = os.getenv('EMAIL_PASS')
	email_to = os.getenv('EMAIL_TO')

	if not email_user or not email_pass or not email_to:
		print('[ERROR] 邮件配置不完整')
		return False

	# 构建测试 HTML 内容
	test_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	test_title = 'AnyRouter HTML 签到测试'

	html_content = f"""
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
			<h1>{test_title}</h1>
			<p>{test_time}</p>
		</div>

		<div class="email-content">
			<div class="account-card">
				<div class="account-header">
					<span class="account-name">测试账号1</span>
					<span class="status-badge" style="background-color: #d1fae5; color: #10b981;">
						✓ 签到成功
					</span>
				</div>
				<div class="balance-info">💰 Current balance: $25.00, Used: $5.00</div>
			</div>

			<div class="account-card">
				<div class="account-header">
					<span class="account-name">测试账号2</span>
					<span class="status-badge" style="background-color: #d1fae5; color: #10b981;">
						✓ 签到成功
					</span>
				</div>
				<div class="balance-info">💰 Current balance: $100.00, Used: $20.00</div>
			</div>

			<div class="stats-section">
				<div class="stats-grid">
					<div class="stat-item">
						<div class="stat-label">总计</div>
						<div class="stat-value">2</div>
					</div>
					<div class="stat-item">
						<div class="stat-label">成功</div>
						<div class="stat-value">2</div>
					</div>
					<div class="stat-item">
						<div class="stat-label">失败</div>
						<div class="stat-value">0</div>
					</div>
				</div>
			</div>
		</div>

		<div class="email-footer">
			<p>此邮件由 AnyRouter 自动签到系统发送</p>
			<p style="margin-top: 4px;">测试邮件 - {test_time}</p>
		</div>
	</div>
</body>
</html>"""

	print('[SENDING] 正在发送 HTML 邮件...')

	kit = NotificationKit()
	try:
		kit.send_email(test_title, html_content, msg_type='html')
		print('[SUCCESS] HTML 邮件发送成功！')
		return True
	except Exception as e:
		print(f'[ERROR] HTML 邮件发送失败: {e}')
		return False


def main():
	print('=' * 60)
	print('AnyRouter 邮件发送测试工具')
	print('=' * 60)
	print()

	if len(sys.argv) > 1:
		mode = sys.argv[1]
		if mode == 'html':
			success = test_html_email()
		else:
			print(f'[ERROR] 未知参数: {mode}')
			print('[INFO] 使用方法: python test_email.py [html]')
			success = False
	else:
		success = test_email_only()

	print()
	print('=' * 60)
	if success:
		print('[COMPLETE] 测试完成')
	else:
		print('[FAILED] 测试失败')
	print('=' * 60)

	sys.exit(0 if success else 1)


if __name__ == '__main__':
	main()
