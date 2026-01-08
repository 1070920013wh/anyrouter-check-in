import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv

# 添加项目根目录到 PATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / '.env')

from utils.notify import NotificationKit


@pytest.fixture
def notification_kit():
	# 每次测试都创建新实例，避免环境变量污染
	return NotificationKit()


def test_real_notification():
	"""真实接口测试，需要配置.env.local文件"""
	if os.getenv('ENABLE_REAL_TEST') != 'true':
		pytest.skip('未启用真实接口测试')

	kit = NotificationKit()
	kit.push_message('测试消息', f'这是一条测试消息\n发送时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')


@patch('smtplib.SMTP_SSL')
@patch('smtplib.SMTP')
def test_send_email(mock_smtp, mock_smtp_ssl):
	# 设置环境变量以通过验证
	os.environ['EMAIL_USER'] = 'test@example.com'
	os.environ['EMAIL_PASS'] = 'password'
	os.environ['EMAIL_TO'] = 'to@example.com'

	mock_server = MagicMock()
	mock_smtp_ssl.return_value = mock_server

	kit = NotificationKit()
	kit.send_email('测试标题', '测试内容')

	# 验证 SMTP_SSL 被调用
	assert mock_smtp_ssl.called
	# 验证 login 和 send_message 被调用
	assert mock_server.login.called
	assert mock_server.send_message.called
	assert mock_server.quit.called


@patch('httpx.Client')
def test_send_pushplus(mock_client_class):
	os.environ['PUSHPLUS_TOKEN'] = 'test_token'

	mock_client_instance = MagicMock()
	mock_client_class.return_value.__enter__.return_value = mock_client_instance

	kit = NotificationKit()
	kit.send_pushplus('测试标题', '测试内容')

	assert mock_client_instance.post.called


@patch('httpx.Client')
def test_send_dingtalk(mock_client_class):
	os.environ['DINGDING_WEBHOOK'] = 'https://oapi.dingtalk.com/test'

	mock_client_instance = MagicMock()
	mock_client_class.return_value.__enter__.return_value = mock_client_instance

	kit = NotificationKit()
	kit.send_dingtalk('测试标题', '测试内容')

	assert mock_client_instance.post.called


@patch('httpx.Client')
def test_send_feishu(mock_client_class):
	os.environ['FEISHU_WEBHOOK'] = 'https://feishu.example.com/test'

	mock_client_instance = MagicMock()
	mock_client_class.return_value.__enter__.return_value = mock_client_instance

	kit = NotificationKit()
	kit.send_feishu('测试标题', '测试内容')

	assert mock_client_instance.post.called


@patch('httpx.Client')
def test_send_wecom(mock_client_class):
	os.environ['WEIXIN_WEBHOOK'] = 'https://weixin.example.com/test'

	mock_client_instance = MagicMock()
	mock_client_class.return_value.__enter__.return_value = mock_client_instance

	kit = NotificationKit()
	kit.send_wecom('测试标题', '测试内容')

	assert mock_client_instance.post.called


@patch('httpx.Client')
def test_send_gotify(mock_client_class):
	os.environ['GOTIFY_URL'] = 'https://gotify.example.com/message'
	os.environ['GOTIFY_TOKEN'] = 'test_token'

	mock_client_instance = MagicMock()
	mock_client_class.return_value.__enter__.return_value = mock_client_instance

	kit = NotificationKit()
	kit.send_gotify('测试标题', '测试内容')

	expected_url = 'https://gotify.example.com/message?token=test_token'
	expected_data = {'title': '测试标题', 'message': '测试内容', 'priority': 9}

	mock_client_instance.post.assert_called_once_with(expected_url, json=expected_data)


@patch('httpx.Client')
def test_send_telegram(mock_client_class):
	os.environ['TELEGRAM_BOT_TOKEN'] = 'test_bot_token'
	os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_id'

	mock_client_instance = MagicMock()
	mock_client_class.return_value.__enter__.return_value = mock_client_instance

	kit = NotificationKit()
	kit.send_telegram('测试标题', '测试内容')

	assert mock_client_instance.post.called


def test_missing_config():
	os.environ.clear()
	kit = NotificationKit()

	with pytest.raises(ValueError, match='Email configuration not set'):
		kit.send_email('测试', '测试')

	with pytest.raises(ValueError, match='PushPlus Token not configured'):
		kit.send_pushplus('测试', '测试')


@patch('utils.notify.NotificationKit.send_email')
@patch('utils.notify.NotificationKit.send_dingtalk')
@patch('utils.notify.NotificationKit.send_wecom')
@patch('utils.notify.NotificationKit.send_pushplus')
@patch('utils.notify.NotificationKit.send_feishu')
@patch('utils.notify.NotificationKit.send_gotify')
def test_push_message(mock_gotify, mock_feishu, mock_pushplus, mock_wecom, mock_dingtalk, mock_email):
	os.environ['EMAIL_USER'] = 'test@example.com'
	os.environ['EMAIL_PASS'] = 'password'
	os.environ['EMAIL_TO'] = 'to@example.com'

	kit = NotificationKit()
	kit.push_message('测试标题', '测试内容')

	assert mock_email.called
	assert mock_dingtalk.called
	assert mock_wecom.called
	assert mock_pushplus.called
	assert mock_feishu.called
	assert mock_gotify.called


@patch('utils.notify.format_html_email')
def test_push_message_with_html(mock_format_html):
	"""测试带 execution_time 参数的 push_message 会调用 format_html_email"""
	os.environ['EMAIL_USER'] = 'test@example.com'
	os.environ['EMAIL_PASS'] = 'password'
	os.environ['EMAIL_TO'] = 'to@example.com'

	mock_format_html.return_value = '<html>test</html>'

	kit = NotificationKit()
	kit.push_message('测试标题', '测试内容', execution_time='2024-01-01 12:00:00')

	# 验证 HTML 格式化函数被调用
	mock_format_html.assert_called_once_with('测试标题', '测试内容', '2024-01-01 12:00:00')
