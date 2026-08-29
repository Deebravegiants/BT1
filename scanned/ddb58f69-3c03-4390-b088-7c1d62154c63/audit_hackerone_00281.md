# [H] GarlicRust - heartbleed style vulnerability in major I2P C++ router implementations

## Summary
Severity: High (CVSS 7.7)
Program: Internet Bug Bounty
Weakness: Buffer Over-read
Reporter: aerodudrizzt
State: resolved
Disclosed: 2019-11-12T23:45:56.450Z
CVE: CVE-2017-17066
Source: https://hackerone.com/reports/295740

## Details
Brief
-----
I2pd and kovri are both C++ I2P routers that share the same code base, as kovri was forked from i2pd several years ago. The vulnerability lies in a common code piece, making both implementations vulnerable, as was acknowledged by orignal, the main developer of i2pd.
The vulnerability is that there is lack of sanitation checks when handling Garlic messages in the both routers: by sending a specially crafted Garlic message, an attacker can cause the router to send onward an I2P message containing leaked RAM data, triggering a massive (up to ~16KB) information leakage.

Technical Details:
===========
Code Version: Taken from Kovri Github on the 18th of November 2017
Commit 5aafe6608519d31e537c97b24ea7b23aa372dd5b
Vulnerable File: src\core\router\garlic.h
Vulnerable Function: GarlicDestination::HandleGarlicPayload
The function is responsible to parse and handle Garlic Payloads: several independent Garlic Cloves.
When handling a clove with a delivery type of "DeliveryTypeTunnel" there are insufficient checks on the message, before it is wrapped and sent onward:
```cpp
    GarlicDeliveryType delivery_type = (GarlicDeliveryType)((flag >> 5) & 0x03);
    switch (delivery_type) {
      case eGarlicDeliveryTypeLocal:
        LOG(debug) << "GarlicDestination: Garlic type local";
        HandleI2NPMessage(buf, len, from);
      break;
      case eGarlicDeliveryTypeDestination:
        LOG(debug) << "GarlicDestination: Garlic type destination";
        buf += 32;  // destination. check it later or for multiple destinations
        HandleI2NPMessage(buf, len, from);
      break;
      case eGarlicDeliveryTypeTunnel: {
        LOG(debug) << "GarlicDestination: Garlic type tunnel";
        // gateway_hash and gateway_tunnel sequence is reverted
        std::uint8_t* gateway_hash = buf;
        buf += 32;
        std::uint32_t gateway_tunnel = bufbe32toh(buf);
        buf += 4;
        std::shared_ptr<kovri::core::OutboundTunnel> tunnel;
        if (from && from->GetTunnelPool())
          tunnel = from->GetTunnelPool()->GetNextOutboundTunnel();
        // EI [BUG-TRACE] : The payload length is based on an unchecked length field
        // EI             : from the just found I2NP message contained in the clove.
        // EI             : When creating and sending this message onward we may leak
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/295740_
