## Title
Webhook shop-domain header is not covered by the HMAC signature, allowing shop-identity spoofing on webhook delivery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` authenticates an inbound webhook by validating the HMAC over the raw request body only, while the `shop` (tenant identity) is read from the `X-Shopify-Shop-Domain` header, which is never included in the signed material. This breaks the identity binding: **`shop` authenticated by HMAC` ≠ `shop` delivered to the handler as the tenant key**. Since Shopify signs all webhooks for every installed shop with the *same* app-level `client_secret` (`Context.api_secret_key`), any party capable of capturing one valid webhook delivery (e.g., from their own shop, where they are a legitimate installer of the app) can replay that exact body with an attacker-chosen `shop-domain` header, and the HMAC check will still pass.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `hmac` is derived purely from the `hmac-sha256` header value; the `shop`, `topic`, and other headers are excluded from the signed content: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., the body) and compares it against the provided `hmac`: [3](#0-2) 

`Webhooks::Registry.process` only checks this body-only HMAC before dispatching the event to the app's handler using `request.shop` as the tenant identifier, with no secondary binding between the validated bytes and the claimed shop: [4](#0-3) 

Because `Context.api_secret_key` is the single app-level secret shared across every shop that installs the app (it is not per-shop), the HMAC only proves "this body was signed by *some* installation of this app" — it proves nothing about *which* shop. An attacker who is themselves a legitimate (even free/trial) installer of the target app receives real, validly-signed webhook deliveries for their own shop. They can capture the raw body + HMAC of one such delivery and resend it (via any endpoint that accepts webhook POSTs, e.g., a test/staging endpoint, or directly if the app forwards to a public callback) with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain. `Utils::HmacValidator.validate` will still return `true`, because the signed content (raw body) and secret are unchanged. `Registry.process` will happily hand `WebhookMetadata.new(..., shop: request.shop, ...)` — now containing the attacker-controlled domain — to the app's handler, exactly as if it were an authentic event from the victim shop.

This is precisely the "shop authenticated versus shop stored as/used-as tenant/session key" mismatch class: the byte range actually verified by the cryptographic check (`raw_body`) is disjoint from the byte range (`shop-domain` header) that the rest of the system treats as authenticated tenant identity.

### Impact Explanation
This qualifies as cross-tenant access (Critical): an attacker can inject events that the host application will process as if they originated from a shop they do not control and were never granted access to. Depending on how the host app's webhook handler uses `WebhookMetadata#shop` (e.g., to look up/create records, trigger data sync, or make API calls scoped to that shop's session), this allows cross-tenant data confusion or forged actions attributed to a victim merchant, without possessing that merchant's access token or the app's `client_secret`.

### Likelihood Explanation
Exploitability requires only that the attacker be able to install the target app on at least one shop they control (a low bar for many public apps) to obtain one legitimate signed webhook body+HMAC pair, plus the ability to POST to the webhook-processing endpoint with a modified `shop-domain` header — both realistic for an unprivileged internet user, and require no leaked secrets or privileged access.

### Recommendation
- Bind the shop identity into the signed material verified by this gem, or independently verify that the `shop-domain` header corresponds to a shop actually associated with a completed OAuth/token-exchange for this app installation before dispatching to the handler.
- At minimum, document and/or enforce that `WebhookMetadata#shop` must not be trusted as an authenticated tenant key on its own; require the host application to cross-check it against a known, previously-authenticated session for that shop.
- Consider constrained verification, similar to the analog report's guidance ("constrain all values used for authorization to their canonical/verified form before use"): treat `request.shop` as untrusted until corroborated by data that is actually covered by the signature or by a separate trust anchor (e.g., stored session/shop mapping).

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` (a shop the attacker controls) so Shopify begins sending real webhooks to the app's webhook endpoint, signed with the app's single `client_secret`.
2. Capture one such delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Replay the same `B` and `H` to the webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `B` and `H`: [5](#0-4) 
5. `ShopifyAPI::Webhooks::Registry.process` dispatches to the app handler with `shop: "victim-shop.myshopify.com"`, `body: JSON.parse(B)` — content the attacker fully controls but now falsely attributed to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-10)
```ruby
      sig { override.returns(String) }
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-21)
```ruby
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
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
