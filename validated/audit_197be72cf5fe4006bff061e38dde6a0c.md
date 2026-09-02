### Title
Webhook Shop-Domain Spoofing via HMAC Coverage Gap — Cross-Tenant Handler Confusion ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The bug class from the external report (using an ETH-transfer primitive that isn't gated by a proper check) maps here to a binding gap between the data that is **cryptographically authenticated** and the data that is **acted upon**. `ShopifyAPI::Webhooks::Request#to_signable_string` only covers the raw body, while `shop`, `topic`, `webhook_id`, and `api_version` are taken verbatim from unauthenticated HTTP headers and then trusted by `Registry.process`.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`. Its `to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` values are all read directly from HTTP headers, none of which are included in the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the body only (`Utils::HmacValidator.validate`, which hashes `to_signable_string`, i.e. the body), and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to construct `WebhookMetadata` passed straight to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` confirms the HMAC covers only `verifiable_query.to_signable_string` (the body), computed with the app's shared `api_secret_key`: [4](#0-3) 

`WebhookMetadata.shop` is a plain, unauthenticated `String` field consumed by the handler as the tenant identifier: [5](#0-4) 

The identity binding that is broken is: **`shop` header value used by the handler to select the tenant ≠ `shop` value actually covered by the HMAC (none)**. Since the same `api_secret_key` is used to sign webhooks for *every* shop that has installed a given app, any body+HMAC pair that is valid for one shop's webhook is *also* a cryptographically valid pair for a forged request bearing an arbitrary `shop-domain` header — the signature says nothing about which shop it was for.

### Impact Explanation
An attacker who installs the target app on their own (attacker-controlled) shop receives genuine Shopify webhooks with valid HMACs computed over bodies they fully control the timing/context of. Because the HMAC never binds the `shop-domain` header, the attacker can replay that same body+HMAC to the app's webhook endpoint while substituting a victim shop's domain in the `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will pass (body/HMAC pair is legitimately signed by the shared secret), and `Registry.process` will dispatch `WebhookMetadata` claiming the event happened on the victim's shop. If the host app's handler uses `data.shop` to look up records, grant entitlements, trigger side effects, or select which tenant's data to mutate, this results in cross-tenant confusion/cross-tenant action — one tenant forging events attributed to another tenant purely by controlling an unauthenticated header, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Any developer/merchant who can install the app (a normal unprivileged flow, not requiring `api_secret_key`, tokens, or any privileged Shopify access) can obtain valid signed webhook bodies for their own shop and immediately has everything needed to forge the `shop`-tagged request; no additional secrets are required beyond what any regular merchant installing the app already possesses.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them to the HMAC), matching the approach already used by `Auth::Oauth::AuthQuery#to_signable_string`, which folds all identity-relevant fields into the signed payload: [6](#0-5) 
At minimum, document/enforce that consuming apps must independently verify `data.shop` against their own installed-shop records before trusting it, since the gem currently provides no cryptographic guarantee for that field.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, obtaining a real webhook delivery: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid over `B` with the app's shared `api_secret_key`).
2. Attacker replays a POST to the app's webhook endpoint with the same raw body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and any `X-Shopify-Topic`.
3. `Webhooks::Request#hmac`/`#to_signable_string` only look at the body, so `Utils::HmacValidator.validate` returns `true`. [7](#0-6) 
4. `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` to the app's handler, which the host app cannot distinguish from a genuine victim-shop event.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-23)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
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
