# [M] Cross-Site-Scripting attack on `<RichTextField>`

## Summary
Severity: Medium
Advisory: GHSA-5jcr-82fh-339v
CVE: CVE-2023-25572
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-14
Source: https://github.com/advisories/GHSA-5jcr-82fh-339v
Type: github-advisory

## Affected
- npm: `react-admin` — affected >=0 <3.19.12
- npm: `react-admin` — affected >=4.0.0 <4.7.6
- npm: `ra-ui-materialui` — affected >=4.0.0 <4.7.6
- npm: `ra-ui-materialui` — affected >=0 <3.19.12

## Details
### Impact

All React applications built with react-admin and using the `<RichTextField>` are affected. 

`<RichTextField>` outputs the field value using `dangerouslySetInnerHTML` without client-side sanitization. If the data isn't sanitized server-side, this opens a possible Cross-Site-Scripting (XSS) attack. 

Proof of concept:

```jsx
import { RichTextField } from 'react-admin';

const record = {
    id: 1,
    body: `
<p>
<strong>War and Peace</strong> is a novel by the Russian author
<a href="https://en.wikipedia.org/wiki/Leo_Tolstoy" onclick="document.getElementById('stolendata').value='credentials';">Leo Tolstoy</a>,
published serially, then in its entirety in 1869.
</p>
<p onmouseover="document.getElementById('stolendata').value='credentials';">
It is regarded as one of Tolstoy's finest literary achievements and remains a classic of world literature.
</p>
<img src="x" onerror="document.getElementById('stolendata').value='credentials';" />
`,
};

const VulnerableRichTextField = () => (
    <>
        <RichTextField record={record} source="body" />
        <hr />
        <h4>Stolen data:</h4>
        <input id="stolendata" defaultValue="none" />
    </>
);
```

### Patches

Versions 3.19.12 and 4.7.6 now use `DOMPurify` to escape the HTML before outputting it with React and `dangerouslySetInnerHTML`

### Workarounds

You don't need to upgrade if you already sanitize HTML data server-side. 

Otherwise, you'll have to replace the `<RichTextField>` by a custom field doing sanitization by hand:

```tsx
// react-admin v4
import * as React from 'react';
import { memo } from 'react';
import PropTypes from 'prop-types';
import get from 'lodash/get';
import Typography from '@material-ui/core/Typography';
import { useRecordContext, sanitizeFieldRestProps, fieldPropTypes } from 'react-admin';
import purify from 'dompurify';

export const removeTags = (input) =>
    input ? input.replace(/<[^>]+>/gm, '') : '';

const RichTextField = memo(
    props => {
        const { className, emptyText, source, stripTags, ...rest } = props;
        const record = useRecordContext(props);
        const value = get(record, source);

        return (
            <Typography
                className={className}
                variant="body2"
                component="span"
                {...sanitizeFieldRestProps(rest)}
            >
                {value == null && emptyText ? (
                    emptyText
                ) : stripTags ? (
                    removeTags(value)
                ) : (
                    <span
                        dangerouslySetInnerHTML={{
                            __html: purify.sanitize(value),
                        }}
                    />
                )}
            </Typography>
        );
    }
);

RichTextField.defaultProps = {
    addLabel: true,
    stripTags: false,
};

RichTextField.propTypes = {
    // @ts-ignore
    ...Typography.propTypes,
    ...fieldPropTypes,
    stripTags: PropTypes.bool,
};

RichTextField.displayName = 'RichTextField';

export default RichTextField;
```

### References

https://github.com/marmelab/react-admin/pull/8644, https://github.com/marmelab/react-admin/pull/8645

## References
- https://github.com/marmelab/react-admin/security/advisories/GHSA-5jcr-82fh-339v
- https://nvd.nist.gov/vuln/detail/CVE-2023-25572
- https://github.com/marmelab/react-admin/pull/8644
- https://github.com/marmelab/react-admin/pull/8645
- https://github.com/marmelab/react-admin
- https://github.com/marmelab/react-admin/releases/tag/v3.19.12
- https://github.com/marmelab/react-admin/releases/tag/v4.7.6
