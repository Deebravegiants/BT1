The docs at `docs/usage/webhooks.md:14` explicitly state: "This will verify the request did indeed come from Shopify" — but that verification only covers the raw body, not the `shop` field that the gem hands to the handler as trusted tenant identity. This confirms the finding is a genuine defect in the gem's own guarantee, not documented as a caveat, and is squarely in scope.

### Title
Webhook shop identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while `ShopifyAPI::Utils::HmacValidator.validate` (invoked by `ShopifyAPI::Webhooks::Registry.process`) only verifies the HMAC over the raw request body via `Request#to_signable_string`. The `shop` value is never included in the signed bytes, so an attacker who can produce any single valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key` (e.g. from a webhook legitimately delivered to a shop they themselves installed the app on) can replay that same body/HMAC pair to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header, and it will pass verification and be dispatched to the handler as if it originated from that other shop.

### Finding Description
The identity binding that should hold is:

`shop value trusted by the handler (WebhookMetadata#shop) == shop value cryptographically bound by the HMAC signature`

This does not hold. Trace through the code:

- `Request#shop` reads the shop identity purely from a header, never touched by any cryptography: [1](#0-0) 
- `Request#to_signable_string`, the value the HMAC is computed over via `VerifiableQuery`, returns only the raw JSON body — the `shop` header is excluded: [2](#0-1) 
- `Registry.process` validates only this HMAC-over-body, then immediately trusts `request.shop` (the header) to build `WebhookMetadata` and dispatches it to the app's handler: [3](#0-2) 
- `HmacValidator.validate`/`validate_signature` compute the signature strictly from `verifiable_query.to_signable_string`, i.e. the body only: [4](#0-3) 
- The `WebhookMetadata#shop` value is delivered to the host application's handler as a trusted field, and the gem's own docs claim `Registry.process` "will verify the request did indeed come from Shopify": [5](#0-4) 

Because the `api_secret_key` is a single shared secret for the whole app (across every shop that installs it), a legitimate `(body, hmac)` pair from any shop the attacker controls is valid for every shop. The gem gives the host app no way to detect that the `shop` header was swapped, since it was never part of the signed material and the gem's `process` method offers no cross-check between body content and header.

### Impact Explanation
This breaks the tenant isolation guarantee the gem is supposed to provide via HMAC verification, enabling cross-tenant access: an attacker who is a merchant on shop A (a completely unprivileged, ordinary user of the app) can capture one valid webhook delivery to their own store and replay it to the app's webhook endpoint while claiming to be shop B. Any host application that trusts `WebhookMetadata#shop` (exactly as the gem's own documentation and example handler recommend) will process attacker-controlled data as if it originated from shop B — for example injecting fabricated `orders/create` or `customers/data_request`/`customers/redact` events into shop B's tenant data, corrupting per-shop state, or triggering shop-B-scoped side effects using attacker-supplied content. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High. Exploitation requires no privileged access, no leaked secret, and no session — only: (1) installing the app on a store the attacker controls (the normal, expected way to use any Shopify app), (2) capturing one legitimately delivered webhook body and its `X-Shopify-Hmac-Sha256` header, and (3) POSTing that same body/HMAC pair to the target app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header. The webhook endpoint is, by design, a public HTTP endpoint reachable by anyone.

### Recommendation
Bind the shop identity into the verified material instead of trusting an unauthenticated header:
- Include the `shop-domain` (and ideally `webhook-id`/`topic`) header value in the string that is HMAC-verified, or
- Cross-validate `request.shop` against a shop value embedded in the (already-signed) body when the topic's payload contains one, or
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and host apps must independently verify it belongs to a shop with an active, valid session/install record before trusting it for any tenant-scoped action, and update `Registry.process`/`docs/usage/webhooks.md` to no longer imply full authenticity of all `WebhookMetadata` fields.

### Proof of Concept
```ruby
# Step 1: Attacker installs the target app on their own shop "attacker.myshopify.com"
# and triggers e.g. an orders/create webhook. Shopify signs it with the app's
# single shared api_secret_key and delivers it with headers:
#   X-Shopify-Topic: orders/create
#   X-Shopify-Hmac-Sha256: <valid HMAC over body B>
#   X-Shopify-Shop-Domain: attacker.myshopify.com
# Attacker records body B and the HMAC exactly as received.

# Step 2: Attacker replays the identical body/HMAC to the app's public
# webhook endpoint, only changing the shop-domain header to the victim shop:
require "net/http"
uri = URI("https://victim-app.example.com/callback/orders/create")
req = Net::HTTP::Post.new(uri)
req.body = body_B # unchanged, attacker-controlled content from their own store
req["X-Shopify-Topic"] = "orders/create"
req["X-Shopify-Hmac-Sha256"] = captured_hmac_from_step_1 # unchanged, still valid!
req["X-Shopify-Shop-Domain"] = "victim-shop.myshopify.com" # forged
Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |http| http.request(req) }

# Server-side, this passes verification because HmacValidator only checks
# body B against the HMAC (lib/shopify_api/utils/hmac_validator.rb#validate_signature,
# lib/shopify_api/webhooks/request.rb#to_signable_string). Registry.process then
# builds WebhookMetadata with shop: "victim-shop.myshopify.com" and hands it to the
# app's WebhookHandler.handle, which the docs instruct developers to trust as the
# originating shop (lib/shopify_api/webhooks/webhook_handler.rb, docs/usage/webhooks.md:14).
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
