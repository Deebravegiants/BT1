This confirms the analysis: `Utils::HmacValidator.validate(request)` at `lib/shopify_api/webhooks/registry.rb:190` only checks the request's `to_signable_string`, which for `Webhooks::Request` is defined at `lib/shopify_api/webhooks/request.rb:35-38` as simply `@raw_body` — the raw JSON body. The `shop-domain` header, read via `request.shop` at `lib/shopify_api/webhooks/request.rb:20-23`, is never included in the HMAC-signed content, yet it is passed straight through as the tenant identifier to the handler at `lib/shopify_api/webhooks/registry.rb:198-199`. This is exactly the "field acted on but not covered by the HMAC" analog: the `shop-domain` header is trusted/acted upon for tenant attribution, but the HMAC (computed only over `@raw_body`) provides no binding between that header and the signed content.

### Title
Webhook `shop-domain` header is trusted for tenant attribution but is not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw request body, then hands the value of the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header straight to the app's webhook handler as the authoritative tenant identifier. That header is never part of the HMAC-signed content.

### Finding Description
`ShopifyAPI::Webhooks::Request` reads `shop` directly from an HTTP header at [1](#0-0) , and computes the HMAC signature input purely from the raw body at [2](#0-1) . `Registry.process` validates that HMAC via `Utils::HmacValidator.validate(request)` at [3](#0-2) , and `HmacValidator.validate_signature` computes the comparison signature from `verifiable_query.to_signable_string` — i.e. the raw body only — at [4](#0-3) . Once the body's HMAC checks out, `request.shop` (the unauthenticated header value) is forwarded unchanged as the `shop:` field of `WebhookMetadata` passed to the app's handler at [5](#0-4) .

The equality that should hold is: `shop that the HMAC-signed body was generated for == shop attributed to the request by the gem`. In this implementation that equality is never checked — the gem verifies "these bytes (body) were signed with our shared secret" but separately trusts "this string (header) tells you which tenant it's for" with no cryptographic link between the two. Since the app's `api_secret_key` is a single shared secret across every shop that installs the app (not per-shop), any legitimate installer of the app — an unprivileged, otherwise-unprivileged merchant/tester who can trigger a real webhook to their own endpoint and observe a genuine `(raw_body, hmac)` pair signed with that shared secret — can replay the same raw body and HMAC to the app's webhook endpoint while substituting the `shop-domain` header for a different (victim) shop's domain. `Registry.process` will not detect this: the HMAC still validates (it never covered the header), and the handler receives `data.shop` set to the attacker-chosen domain alongside `data.body` content that is real, HMAC-valid data.

### Impact Explanation
This breaks the tenant/shop identity binding relied upon by every consumer of `WebhookMetadata#shop`: a webhook is validated for content authenticity but not for which store it actually came from. Any app whose webhook handler uses `data.shop` to select a session, tenant record, or downstream side effect (exactly the pattern shown in the gem's own documentation and tests, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)` in `docs/usage/webhooks.md:26`) can be made to apply attacker-supplied, HMAC-"valid" webhook content under a different shop's identity — a cross-tenant confusion enabled purely by a gap in what the gem's HMAC covers versus what it trusts.

### Likelihood Explanation
Exploitation requires only the ability to install the target app on any shop (or otherwise obtain one legitimate, correctly-signed webhook body/HMAC pair for that app) and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header — no possession of `api_secret_key`, access tokens, or any privileged credential is required, since the shared secret is never disclosed to the attacker, only reused by them via a legitimately-signed payload.

### Recommendation
Do not treat `request.shop` as authenticated on its own. At minimum, `Utils::HmacValidator`/`Webhooks::Request#to_signable_string` should incorporate the shop-domain (and ideally topic/webhook-id) into the signed material it verifies, or `Registry.process` should independently corroborate the header's shop against a known/installed-shop record (e.g. a stored session) before dispatching to the handler, rather than passing the raw header value straight into `WebhookMetadata`.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop `attacker.myshopify.com`, causing Shopify to send a legitimate webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Capture `(B, HMAC(secret, B))` from that legitimate delivery (attacker fully controls what triggers this on their own shop, so `B` can be shaped to contain attacker-chosen data, e.g. an `orders/create` payload with attacker-chosen fields).
3. Replay a POST to the same webhook endpoint with the identical body `B` and identical `X-Shopify-Hmac-Sha256` value, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:26-31` succeeds because it only re-derives the signature from `B` via `to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`), which is unchanged.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) dispatches to the app's handler with `data.shop == "victim.myshopify.com"` and `data.body == B`, even though this content never originated from Shopify on behalf of `victim.myshopify.com`.

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
