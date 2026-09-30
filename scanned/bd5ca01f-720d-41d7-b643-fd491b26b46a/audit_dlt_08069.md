# [?] p2p/discv5: fix topic register panic at shutdown (#15946)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-01-23
Source: https://github.com/celo-org/celo-blockchain/commit/397c6cde1e2fd3636024cad5d23d5e06796772dc
Type: security-commit

## Details
p2p/discv5: fix topic register panic at shutdown (#15946)

## Patch
### p2p/discv5/ticket.go
```diff
@@ -350,7 +350,7 @@ func (s *ticketStore) nextFilteredTicket() (*ticketRef, time.Duration) {
 
 		regTime := now + mclock.AbsTime(wait)
 		topic := ticket.t.topics[ticket.idx]
-		if regTime >= s.tickets[topic].nextReg {
+		if s.tickets[topic] != nil && regTime >= s.tickets[topic].nextReg {
 			return ticket, wait
 		}
 		s.removeTicketRef(*ticket)
```
