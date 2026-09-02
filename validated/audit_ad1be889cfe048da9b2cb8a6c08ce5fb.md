### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop` (tenant identity) attribute is read from an unauthenticated HTTP header. `ShopifyAPI::Utils::HmacValidator` verifies only that signable string, so the `shop` value handed to the host application's webhook handler is never bound to the HMAC that "authenticates" the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` and compares it to the supplied `hmac`: [3](#0-2) 

`Registry.process` accepts any request whose body-only HMAC validates, then forwards the *unverified* `request.shop` value straight to the app-defined handler as the tenant identity for the event: [4](#0-3) 

This is the same identity-binding defect class as the referenced report: the field the system *acts on* for tenant attribution (`shop`/`from_address`-equivalent) is not the field the authentication mechanism actually covers (HMAC only signs the body, analogous to Cairo's event committing to `tx.origin` rather than the caller). By contrast, the OAuth flow does bind `shop` into the signed payload, showing the correct pattern is available and simply wasn't applied to webhooks: [5](#0-4) 

Equality that should hold but doesn't: `shop used for tenant attribution == shop cryptographically bound by hmac`. Instead: `shop used for tenant attribution == shop header value (attacker controlled, unauthenticated)`, while `hmac binds only == raw_body`.

### Impact Explanation
Any merchant that has the app installed on their own store legitimately receives real webhook deliveries from Shopify, each with a valid `hmac-sha256` signature over the body (computed with the app's `client_secret`, which the attacker never needs to know). Because the header carrying the `shop-domain` is excluded from the signed content, that merchant can replay the exact same body + HMAC to the app's webhook endpoint while substituting a different shop's domain in the `shop-domain` header. The gem will accept the request as valid (`Utils::HmacValidator.validate` passes) and hand the host application a `WebhookMetadata` claiming the event belongs to the victim shop. If the host app uses `data.shop` to key data updates (as the gem's own webhook documentation instructs), this results in cross-tenant data corruption/attribution — e.g. injecting fabricated order/customer data into another merchant's records, or spoofing an `app/uninstalled` event for a shop the attacker doesn't own.

### Likelihood Explanation
Exploitation requires no access to the app's `client_secret`, access tokens, or any privileged credential — only the ability to install the app on one's own store (an "unprivileged internet user" relative to the gem's trust boundary) and replay an observed, validly-signed webhook body with a modified `shop-domain` header. This is a realistic and low-effort attack path once the app receiving webhooks is publicly reachable, which is the default deployment model documented for this gem.

### Recommendation
Bind the tenant identity into the authenticated payload before trusting it:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in the HMAC-signable content, or
- Independently verify the header-provided `shop` against a shop identifier embedded in/derived from the verified body (where the topic's payload contains one), and reject mismatches, or
- Require host applications to correlate `WebhookMetadata#shop` against a shop already known/authenticated for that specific webhook subscription rather than trusting the header value implicitly, and update `docs/usage/webhooks.md` to call out this limitation.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed and
# legitimately receives this real Shopify webhook (valid HMAC over the body):
raw_body = '{"id":1,"note":"legit order"}'
real_hmac_header = "shopify-provided-base64-hmac-over-raw_body"

# Attacker replays the same body/HMAC to the app's endpoint, but swaps the
# shop-domain header to a victim shop the attacker does not own/control:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => real_hmac_header,   # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (it only checks raw_body),
#    and the host app's handler receives WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)
#    even though the payload never originated from that shop.
``` [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
