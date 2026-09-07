# [M] SSRF via filter bypass due to lax checking on IPs

## Summary
Severity: Medium
Program: Nextcloud
Weakness: Server-Side Request Forgery (SSRF)
Reporter: obitorasu
State: resolved
Disclosed: 2023-02-10T02:03:11.903Z
Source: https://hackerone.com/reports/1702864

## Details
## Summary:
Hello,

I was reading up on the recent SSRF bug found on NextCloud which is originally a part of this [report](https://hackerone.com/reports/1608039) by @tomorrowisnew_ 

I went through the source code again which was highlighted in the report I mentioned and I noticed that filtering for some of the more advanced SSRF payloads were clearly missing. Alphanumeric payloads came to my mind when thinking about the same so I set up a local test environment with my friend @w1redch4d

We primarily focused on the code around the IP checking namely `ThowIfLocalIp`:
```php
	public function ThrowIfLocalIp(string $ip) : void {
		$localRanges = [
			'100.64.0.0/10', // See RFC 6598
			'192.0.0.0/24', // See RFC 6890
		];
		if (
			(bool)filter_var($ip, FILTER_VALIDATE_IP) &&
			(
				!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) ||
				IpUtils::checkIp($ip, $localRanges)
			)) {
			$this->logger->warning("Host $ip was not connected to because it violates local access rules");
			throw new LocalServerException('Host violates local access rules');
		}

		// Also check for IPv6 IPv4 nesting, because that's not covered by filter_var
		if ((bool)filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6) && substr_count($ip, '.') > 0) {
			$delimiter = strrpos($ip, ':'); // Get last colon
			$ipv4Address = substr($ip, $delimiter + 1);

			if (
				!filter_var($ipv4Address, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) ||
				IpUtils::checkIp($ip, $localRanges)) {
				$this->logger->warning("Host $ip was not connected to because it violates local access rules");
				throw new LocalServerException('Host violates local access rules');
			}
		}
	}
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1702864_
