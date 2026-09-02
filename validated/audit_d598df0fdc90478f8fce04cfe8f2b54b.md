I have enough evidence to complete the analysis. This is a genuine finding: the webhook HMAC only covers the JSON body, while `shop`, `topic`, and `webhook_id` — the fields the host app uses to attribute the event to a tenant — are transmitted as unauthenticated headers.

### Title
Webhook HMAC does not bind the `shop-domain` header, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , so `Utils::HmacValidator.validate` only proves that *some* payload with this exact body content was signed with the app's shared `api_secret_key` [2](#0-1) . The `shop`, `topic`, and `webhook_id` values are read straight from HTTP headers that are never part of the signed string [3](#0-2) , yet `Registry.process` trusts `request.shop` as the tenant identity and hands it to the app's handler unchanged [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop header == shop bound by HMAC signature`. It does not. Only `@raw_body` is fed into `compute_signature` [5](#0-4) ; the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers are parsed independently and passed to `WebhookMetadata` without any cryptographic tie to the body that was verified [6](#0-5) .

Because `api_secret_key` is a single per-app secret shared across every merchant that installs the app (it is not per-shop), any tenant that has legitimately installed the app can capture a real webhook delivery for their own shop (valid body + valid HMAC), then replay that exact body to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop. `HmacValidator.validate` still succeeds because the body and secret are unchanged [2](#0-1) , and `Registry.process` passes the attacker-chosen `shop` straight to the handler as if Shopify itself had attested to it [7](#0-6) . The documented handler contract explicitly tells implementers to treat `data.shop` as trustworthy tenant identification [8](#0-7) , so downstream apps commonly key their tenant-scoped state updates directly off this field.

This satisfies "a field acted on but not covered by the HMAC": the header used to attribute and route the event (`shop`) is decoupled from the cryptographic proof of authenticity, breaking the shop-authenticated-vs-shop-acted-upon equality.

### Impact Explanation
An attacker who is themselves a legitimate (if malicious/compromised) merchant of the target app can forge webhook events that appear to originate from a different, victim shop, without ever obtaining the app's `client_secret` in plaintext or accessing the victim's credentials. Any host application built on this gem that uses `WebhookMetadata#shop` to select/update per-tenant records (the pattern this gem's own docs recommend) can have another tenant's data corrupted, deleted (e.g. `customers/redact`, `shop/redact` mandatory topics), or overwritten with attacker-controlled body content — a cross-tenant access/integrity violation.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own legitimate app installation to obtain one real, validly-signed webhook body/HMAC pair for any topic whose body content the attacker controls or can predict, and (2) the ability to send an arbitrary POST to the app's public webhook endpoint with a forged `shop-domain` header. No access to the app's `api_secret_key`, TLS interception, or victim credentials is required, making this reachable by any unprivileged internet-connected merchant of the app.

### Recommendation
Bind the tenant-identifying headers into the HMAC-covered material, e.g. have `Request#to_signable_string` incorporate `shop`, `topic`, and `webhook_id` alongside the body (or, at minimum, document and enforce that host apps must independently verify `request.shop` against the shop associated with the `Session`/subscription that registered the webhook, rather than trusting the header value directly). Consider exposing a `Registry.process` option that requires callers to pass the expected shop and reject mismatches before invoking the handler.

### Proof of Concept
```ruby
# 1. Attacker has a legitimate install for "attacker-shop.myshopify.com" and receives
#    a real webhook for topic "customers/redact" with some fixed JSON body B, along
#    with the valid HMAC over B (computed with the app's shared api_secret_key).

# 2. Attacker replays the exact same body B and HMAC, but swaps the shop header:
headers = {
  "x-shopify-topic"        => "customers/redact",
  "x-shopify-hmac-sha256"  => captured_valid_hmac_base64, # valid for body B
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id"   => "forged-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body_B, headers: headers)

# 3. Registry.process validates HMAC successfully (only body B is signed) and
#    invokes the app's handler with shop: "victim-shop.myshopify.com".
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "customers/redact", body: parsed_B, ...))
```
The host app's handler, trusting `data.shop` per this gem's documented contract [8](#0-7) , performs a tenant-scoped action (e.g. data redaction/update) against `victim-shop.myshopify.com` on the attacker's behalf.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
