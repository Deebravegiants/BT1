## Title
Webhook shop-domain identity spoofing via unsigned header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , while `Registry.process` uses `request.shop`, which is read from the `X-Shopify-Shop-Domain` HTTP header [2](#0-1) , to identify the tenant that a webhook belongs to before dispatching it to the app's handler [3](#0-2) . The HMAC validation performed by `Utils::HmacValidator.validate` only proves the request body was signed with the app's `api_secret_key`; it says nothing about which shop the header claims to be from [4](#0-3) .

### Finding Description
The identity binding that should hold is: `hmac_signed_bytes == bytes_that_determine_the_tenant(shop)`. In this gem that equality is broken:

- What is HMAC-verified: `@raw_body` only [5](#0-4) .
- What is trusted to select the tenant: the `shopify-shop-domain`/`x-shopify-shop-domain` header, taken verbatim with no cryptographic binding to the body or to the HMAC signature [2](#0-1) .

Because Shopify signs webhooks for an app using the single, app-wide `api_secret_key` (not a per-shop secret), any webhook payload legitimately delivered to the attacker's own installed store (which the attacker can freely receive, since they can install their own app instance / trigger their own store's webhooks) carries a valid HMAC for that same `api_secret_key`. An attacker can then re-POST that captured body+HMAC to the victim app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a different (victim) shop domain. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-derives the HMAC from `@raw_body` and compares against the attacker-supplied header value using `OpenSSL.secure_compare` [6](#0-5) ; it passes because the body is untouched. The forged `shop` is then handed to the handler untouched via `WebhookMetadata.new(... shop: request.shop ...)` [7](#0-6) .

This exactly matches the analog class called out in scope: "a field acted on but not covered by the HMAC" — here the tenant-identifying `shop` field is acted upon by the app's webhook dispatch logic but is not included in `to_signable_string`.

### Impact Explanation
Any app built on this gem that uses `data.shop` from a processed webhook to scope business logic (e.g. per-shop data deletion for the mandatory `shop/redact`/`customers/redact`/`customers/data_request` topics, updating per-shop state, crediting/debiting resources, etc.) can be made to act on behalf of a shop that never actually sent the request. This is a cross-tenant confusion/spoofing primitive: an unprivileged holder of any one valid app webhook (trivially obtainable by installing the app on an attacker-controlled store) can impersonate arbitrary other shops to the app's webhook consumer, without needing the victim's access token or credentials.

### Likelihood Explanation
Exploitation only requires: (1) installing the target app on an attacker-owned development/free store to receive one genuine signed webhook (or capturing any webhook body/HMAC pair for the shared `api_secret_key`), and (2) resending that body with a forged shop header to the app's public webhook endpoint. No secrets, tokens, or privileged access are required, and the vulnerable check (`HmacValidator.validate` against `to_signable_string`) is exactly as implemented in this gem and used unconditionally by `Registry.process`.

### Recommendation
Bind the shop identity into the HMAC-verified surface, or otherwise cryptographically tie the `shop-domain` header to the signed body — e.g. Shopify's own guidance is to also verify the webhook's `shop` domain/`webhook-id` against expected/known-installed shops before trusting it, or include header values relevant to routing (topic, shop-domain) in the signable string used by `HmacValidator`. At minimum, `Webhooks::Registry.process` (or `Request`) should reject/flag webhooks whose `shop` is not verified as consistent with signed data, and should not treat the unauthenticated `X-Shopify-Shop-Domain` header as a trusted tenant identifier on its own.

### Proof of Concept
1. Install the app under test on an attacker-controlled shop `attacker.myshopify.com`; capture a legitimately delivered webhook, e.g. `orders/create`, including its raw body and its `X-Shopify-Hmac-Sha256` header (valid because it is HMAC'd with the app's shared `api_secret_key`).
2. Resend that exact body and HMAC header to the victim app's webhook endpoint, replacing `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and it matches, so `Registry.process` proceeds [3](#0-2) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from `attacker.myshopify.com`, causing the app to process attacker-controlled data as if it belonged to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
