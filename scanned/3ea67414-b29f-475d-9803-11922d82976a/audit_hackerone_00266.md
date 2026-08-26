# [H] Authenticated Code Execution through Phar deserialization in CSV Importer as Shop manager in WooCommerce

## Summary
Severity: High
Program: Automattic
Weakness: Deserialization of Untrusted Data
Reporter: simonscannell
State: resolved
Disclosed: 2019-12-19T14:26:02.746Z
Source: https://hackerone.com/reports/403083

## Details
This vulnerability is based on the following exploitation technique:

https://blog.ripstech.com/2018/new-php-exploitation-technique/

It is easier to explain this vulnerability by having watched the PoC first:
https://www.youtube.com/watch?v=mr3bAOIUwd4

Here is what's happening:

1. Since a valid phar file needs o be uploaded to the server (the extension doesn't matter) I upload the poc.jpg via the media uploader
2. I begin the Import process with a valid CSV file
3.  The importer asks if I am sure that I want to run the import on these files
4. I confirm and modify the  POST parameter to my phar:// wrapper and deserialize the file
5. The PHP code executes

The source of the vulnerability within the source code lies in the /woocommerce/includes/import/class-wc-product-csv-importer.php:

```
	public function __construct( $file, $params = array() ) {
		$default_args = array(
			'start_pos'        => 0, // File pointer start.
			'end_pos'          => -1, // File pointer end.
			'lines'            => -1, // Max lines to read.
			'mapping'          => array(), // Column mapping. csv_heading => schema_heading.
			'parse'            => false, // Whether to sanitize and format data.
			'update_existing'  => false, // Whether to update existing items.
			'delimiter'        => ',', // CSV delimiter.
			'prevent_timeouts' => true, // Check memory and time usage and abort if reaching limit.
			'enclosure'        => '"', // The character used to wrap text in the CSV.
			'escape'           => "\0", // PHP uses '\' as the default escape character. This is not RFC-4180 compliant. This disables the escape character.
		);

		$this->params = wp_parse_args( $params, $default_args );
		$this->file   = $file;

		if ( isset( $this->params['mapping']['from'], $this->params['mapping']['to'] ) ) {
			$this->params['mapping'] = array_combine( $this->params['mapping']['from'], $this->params['mapping']['to'] );
		}
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/403083_
