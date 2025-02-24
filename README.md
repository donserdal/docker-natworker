```
version: '3'
services:
  natworker:
    container_name: natworker
    restart: unless-stopped
    ports:
      - '5000:5000'
    environment:
      - UID=1000
      - GID=1000
      - TZ=Europe/Amsterdam
      - FW_GETENDPOINT=https://<PFsense URL>/api/v1/firewall/nat/port_forwards
      - FW_PATCHENDPOINT=https://<PFsense URL>/api/v1/firewall/nat/port_forward
      - FW_APPLYPOINT=https://<PFsense URL>/api/v1/firewall/apply
      - FW_APIKey=https://<PFsense URL>/api/v1/firewall/nat/port_forward
      - WEBHOOK_URL=https://discord.com/api/webhooks/<ID>/<Auth_KEY>
      - WEBHOOK_TITLE=Webhook Title
      - WEBHOOK_COLOR=Webhook Color
      - WEBHOOK_USER=Webhook User
    image: donserdal/natworker
```
	
	
    
    
    
    
    
    
    
    
    
