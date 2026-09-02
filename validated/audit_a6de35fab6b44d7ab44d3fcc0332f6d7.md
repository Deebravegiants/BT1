### Title
Webhook shop-domain (tenant identity) header is not covered by the HMAC signature, allowing cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw request body only, while the `shop` (and `topic`/`api_version`/`webhook_id`) values are taken from unauthenticated HTTP headers. `Registry.process` validates the HMAC against the body, then trusts `request.shop` as the tenant identity handed to the app's webhook handler, breaking the equality `bytes verified == bytes acted on`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, `#webhook_id` are all read straight from HTTP headers, which are not part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the body via `Utils::HmacValidator.validate(request)`, and — once that check passes — hands `request.shop` (and `request.topic`, `request.api_version`, `request.webhook_id`) to the registered handler as the trusted tenant/event identity: [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the body) against the secret-derived HMAC; it never touches `shop`, `topic`, or the other header-derived fields: [4](#0-3) 

This matches the report's bug class ("a field acted on but not covered by the HMAC"): the signature authenticates the body bytes, but the identity field (`shop`) that the app's handler treats as authoritative comes from headers outside that signature.

### Impact Explanation
An attacker who legitimately receives a Shopify webhook for their own store (e.g. by installing the app on a shop they control, or capturing any previously delivered valid webhook whose HMAC remains valid — HMACs aren't tied to a specific delivery and don't expire) can resend the exact same `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting a different `shopify-shop-domain` header value. `HmacValidator.validate` will still succeed because it only checks the body against the secret, and `Registry.process` will pass the attacker-chosen `shop` value into the handler. If the host application uses `WebhookMetadata#shop` (or `request.shop`) as the tenant key to look up sessions, update records, or attribute customer data (e.g. `customers/data_request`, `orders/create`, etc.), this results in cross-tenant data confusion/injection — the app processes attacker-controlled data as if it belonged to a different, victim shop. This satisfies the "cross-tenant access" Critical impact category, since the tenant boundary (`shop`) is not cryptographically bound to the verified bytes.

### Likelihood Explanation
Medium-High. The attacker needs a validly-signed webhook body for *some* shop (trivially obtainable by installing the app themselves, since app webhook endpoints are typically public HTTP(S) endpoints with no additional caller authentication beyond the HMAC), and then only needs to replay it with a modified header — no access to `client_secret` or any merchant token is required. The main precondition is that the host application actually keys business logic off `WebhookMetadata#shop`/`request.shop` for tenant identification, which is the standard integration pattern this gem's own docs recommend.

### Recommendation
Bind the tenant/event identity to the signed payload rather than trusting headers independently of the HMAC. Options:
- Include `shop`, `topic`, `api_version`, and `webhook_id` in the signable string used for HMAC verification (this would require Shopify to sign over headers too, so may need coordination with Shopify's webhook delivery format), or
- At minimum, cross-check the header-derived `shop` against an app-known set of shops that have valid sessions/registrations before trusting it, and document clearly in `docs/usage/webhooks.md` that `request.shop`/`WebhookMetadata#shop` is **not** covered by the HMAC and must not be treated as authenticated on its own.
- Consider deduplicating/rejecting replayed `webhook_id` values to reduce replay window, since `webhook_id` itself isn't signed either.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com"
# and receives a real webhook delivery, e.g. for "orders/create":
raw_body = '{"id": 1, "note": "malicious payload"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# Attacker resends the same (raw_body, hmac) but swaps the shop-domain header
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- attacker-controlled, unsigned
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds (it only checks raw_body),
# and the handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
# even though the body was never signed for that shop.
``` [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
