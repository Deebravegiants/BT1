### Title
Webhook `shop-domain` Header Not Covered by HMAC Allows Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` authenticates the *body bytes* but never binds the `shop`, `topic`, `webhook-id`, or `api-version` header values. `ShopifyAPI::Webhooks::Registry.process` nonetheless trusts `request.shop` (read straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header) and hands it to the app's webhook handler as the tenant identifier.

### Finding Description
The HMAC binding for inbound webhooks is: [1](#0-0) 

`to_signable_string` only ever returns `@raw_body`. The `shop` accessor, however, is derived independently from a request header that is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` computes an HMAC-SHA256 over `verifiable_query.to_signable_string` (i.e. the raw body only) and compares it with the received HMAC: [3](#0-2) 

`Registry.process` validates only that HMAC, then dispatches to the handler using `request.shop` and `request.parsed_body`, both taken from attacker-controllable inputs whose only cryptographic binding is on the body bytes, not on which shop they are claimed to belong to: [4](#0-3) 

The equality that should hold is: `shop the HMAC authenticates == shop the handler is told the data belongs to`. In this implementation the HMAC authenticates only the body, so this equality does not hold — the `shop-domain` header can be freely substituted by anyone who possesses a body/HMAC pair (e.g. a merchant who receives real webhooks for their own shop, since Shopify signs the body with the single app-wide `api_secret_key` shared across all shops using the app) without invalidating the signature.

### Impact Explanation
Any external party who owns a store connected to the same app (and can therefore trigger/observe a legitimate webhook delivery, or otherwise obtain a valid `body`/HMAC pair for that shared `api_secret_key`) can replay that exact body to the app's webhook endpoint while setting the `x-shopify-shop-domain` header to an arbitrary victim shop domain. `HmacValidator.validate` still succeeds because only the body is checked, and the handler receives `WebhookMetadata` claiming the payload came from the victim shop. Any app logic keyed by `data.shop` (e.g. looking up/mutating per-tenant state, associating the body's contents with the victim's session/store record) is fed attacker-controlled data under a spoofed tenant identity — a cross-tenant data-integrity/confusion issue.

### Likelihood Explanation
The `shop` header is trivial to forge (it's a normal HTTP header of an unauthenticated request), and the shared `api_secret_key` used to sign a body is common to every shop that installed the app, so any of the app's merchants can produce a validly-HMAC'd body for a benign topic/payload of their choosing and immediately reuse it against an arbitrary shop-domain value. No credentials of the victim or Shopify's private keys are required.

### Recommendation
Include the `shop`, `topic`, `webhook-id`, and `api-version` header values in the signable string that is HMAC-verified (or otherwise cryptographically bind the shop identity to the signed payload), so that changing any of these headers invalidates the signature.

### Proof of Concept
1. App merchant A installs the app and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid over `B` with the app's `api_secret_key`), `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker (merchant A) resends the same request to the app's webhook endpoint but replaces the header with `x-shopify-shop-domain: shop-b.myshopify.com` (a victim shop also using the app), keeping `B` and `H` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`== B`) and matches `H` — validation passes.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-supplied data under the victim shop's identity.

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
