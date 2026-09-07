# [M] WPGraphQL Plugin vulnerable to Server Side Request Forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-cfh4-7wq9-6pgg
CVE: CVE-2023-23684
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-cfh4-7wq9-6pgg
Type: github-advisory

## Affected
- Packagist: `wp-graphql/wp-graphql` — affected >=0 <1.14.6

## Details
### Impact
Users with capabilities to upload media (editors and above) are succeptible to SSRF (Server-Side Request Forgery) when executing the `createMediaItem` Mutation. 

Authenticated users making GraphQL requests that execute the `createMediaItem` could pass executable paths in the mutations `filePath` argument that could give them unwarranted access to the server. 

It's recommended to update to WPGraphQL v1.14.6 or newer. If you're unable to do so, below is a snippet you can add to your functions.php (or similar) that filters the `createMediaItem` mutation's resolver. 

### Patches

- [v1.14.6](https://github.com/wp-graphql/wp-graphql/releases/tag/v1.14.6)
- https://github.com/wp-graphql/wp-graphql/pull/2840

### Workarounds
If you're unable to upgrade to v1.14.6 or higher, you should be able to use the following snippet in your functions.php to override the vulnerable resolver. 

This snippet has been tested as far back as WPGraphQL v0.15

```php
add_filter( 'graphql_pre_resolve_field', function( $nil, $source, $args, $context, \GraphQL\Type\Definition\ResolveInfo $info, $type_name, $field_key, $field, $field_resolver ) {

	if ( $info->fieldName !== 'createMediaItem' ) {
		return $nil;
	}

	$input = $args['input'] ?? null;

        if ( ! isset( $input['filePath'] ) ) {
		return $nil;
	}

	$uploaded_file_url   = $input['filePath'];

	// Check that the filetype is allowed
	$check_file = wp_check_filetype( $uploaded_file_url );

	// if the file doesn't pass the check, throw an error
	if ( ! $check_file['ext'] || ! $check_file['type'] || ! wp_http_validate_url( $uploaded_file_url ) ) {
		throw new \GraphQL\Error\UserError( sprintf( __( 'Invalid filePath "%s"', 'wp-graphql' ), $input['filePath'] ) );
	}

	$protocol = wp_parse_url( $input['filePath'], PHP_URL_SCHEME );

	// prevent the filePath from being submitted with a non-allowed protocols
	$allowed_protocols = [ 'https', 'http', 'file' ];

	if ( ! in_array( $protocol, $allowed_protocols, true ) ) {
		throw new \GraphQL\Error\UserError( sprintf( __( 'Invalid protocol. "%1$s". Only "%2$s" allowed.', 'wp-graphql' ), $protocol, implode( '", "', $allowed_protocols ) ) );
	}

	return $nil;

}, 10, 9 );
```

### References

- https://patchstack.com/database/vulnerability/wp-graphql/wordpress-wp-graphql-plugin-1-14-5-server-side-request-forgery-ssrf-vulnerability

## References
- https://github.com/wp-graphql/wp-graphql/security/advisories/GHSA-cfh4-7wq9-6pgg
- https://nvd.nist.gov/vuln/detail/CVE-2023-23684
- https://github.com/wp-graphql/wp-graphql/pull/2840
- https://github.com/wp-graphql/wp-graphql
- https://github.com/wp-graphql/wp-graphql/releases/tag/v1.14.6
- https://patchstack.com/database/vulnerability/wp-graphql/wordpress-wp-graphql-plugin-1-14-5-server-side-request-forgery-ssrf-vulnerability?_s_id=cve
