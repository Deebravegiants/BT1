## Title
Webhook shop/topic identity spoofing via HMAC that only covers the raw body — cross-tenant webhook forgery - (`lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` binds the webhook `hmac-sha256` signature only to the raw HTTP body. The `shop-domain`, `topic`, `api-version`, and `webhook-id` values that `ShopifyAPI::Webhooks::Registry.process` dispatches to application handlers are read straight from unauthenticated HTTP headers and never enter the signed payload. [1](#0-0) 

## Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing `HMAC-SHA256(api_secret_key, to_signable_string)` and comparing it against the supplied `hmac`. [2](#0-1) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body`, while `hmac`, `shop`, `topic`, `api_version`, and `webhook_id` are each pulled independently from HTTP headers (`x-shopify-hmac-sha256`, `x-shopify-shop-domain`, `x-shopify-topic`, etc.) with no cryptographic linkage between them: [3](#0-2) 

`Registry.process` validates only that the raw body's HMAC is correct, then dispatches the handler using the unauthenticated `shop` and `topic` values taken from headers: [4](#0-3) 

The intended identity binding should be:
`hmac == HMAC(secret, raw_body ⊕ shop ⊕ topic)`

but the actual binding implemented is:
`hmac == HMAC(secret, raw_body)`, with `shop`/`topic` parsed independently and never verified.

This is precisely the "bytes verified versus bytes parsed" class described in the report's bug-hint: the app trusts fields (`shop`, `topic`) that were never covered by the cryptographic check that gates processing.

### Exploitability without any privileged credential
An unprivileged attacker who merely installs the target app on their own free/dev store (no special privilege — any internet user can do this) will receive legitimately Shopify-signed webhook deliveries for their own shop: a `(raw_body, hmac)` pair that is valid under the app's real `api_secret_key`, without the attacker ever learning that secret. Because `shop-domain` and `topic` are not part of the signed material, the attacker can capture one such valid `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for any *victim* shop and/or the `x-shopify-topic` header for any registered topic. `Registry.process` will accept it (HMAC check passes, since it's checking only the untouched raw body/hmac pair) and hand `WebhookMetadata.new(topic: <victim/forged topic>, shop: <victim shop>, body: <attacker-controlled parsed body>, ...)` to the application's webhook handler as if it genuinely originated from the victim shop. [5](#0-4) 

## Impact Explanation
This breaks the tenant-isolation boundary the HMAC is supposed to provide: any handler that keys destructive or data-returning actions off `WebhookMetadata#shop` (e.g., mandatory GDPR compliance topics like `customers/redact`, `shop/redact`, `customers/data_request`, or app-specific business logic keyed by shop) can be triggered for an arbitrary target shop by an attacker who controls no more than a throwaway installation of the same app. This is cross-tenant access/action forgery — a Critical-severity outcome under the given impact taxonomy, achieved with no access token, no `api_secret_key`, and no privileged account for the *victim* shop.

## Likelihood Explanation
High. Installing an app on a free development store is trivial and available to any internet user; capturing outgoing webhook headers/body from one's own store requires no special access; and replaying an HTTP POST with modified headers to a public webhook endpoint is a standard capability of any HTTP client. The only "skill" required is understanding that `shop`/`topic` aren't authenticated, which is directly visible from the library's source.

## Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable payload that is verified against the HMAC, or otherwise cryptographically bind them to the request before they are parsed. If Shopify's real webhook HMAC scheme only signs the raw body (as it does), the resolution is: do not trust `shop`/`topic` derived purely from headers for authorization/business decisions unless the receiving application independently re-validates that the webhook subscription (registered per-shop, per-topic, with an app-generated unique callback path/secret) matches the claimed shop/topic — i.e., correlate `webhook_id` against Shopify's Admin API for that specific shop's session before trusting `shop`, rather than trusting the header value as-is.

## Proof of Concept
```ruby
# Attacker legitimately installs `app` on their own store "attacker-shop.myshopify.com"
# and receives a real webhook delivery, e.g. for topic "orders/create":
raw_body = '{"id": 1, "note": "hello"}'
real_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
# app_secret is NEVER known to attacker; this hmac is produced by Shopify itself
# and delivered in the "x-shopify-hmac-sha256" header of the legitimate webhook POST.

# Attacker captures (raw_body, real_hmac) from their own installation, then replays it
# to the SAME app's public webhook endpoint, but swaps the shop/topic headers:
forged_headers = {
  "x-shopify-topic"       => "customers/redact",              # attacker-chosen topic
  "x-shopify-hmac-sha256" => Base64.encode64(real_hmac),        # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",       # forged target shop
  "x-shopify-webhook-id"  => "any-value",
  "x-shopify-api-version" => "2024-01",
}

# HTTP POST body=raw_body, headers=forged_headers  -> app's /webhooks endpoint

req = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(req)
# Utils::HmacValidator.validate(req) succeeds because it only checks raw_body/hmac.
# The registered handler for "customers/redact" now runs with shop == "victim-shop.myshopify.com",
# even though this webhook never originated from victim-shop and was never signed for it.
``` [4](#0-3) [1](#0-0)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
