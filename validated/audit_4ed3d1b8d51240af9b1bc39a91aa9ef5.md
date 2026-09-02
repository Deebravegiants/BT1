I have sufficient evidence to write up the finding now.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing an app-installer to spoof the tenant identity delivered to webhook handlers - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)`. The `Request#to_signable_string` returns only `@raw_body`, so the `x-shopify-shop-domain` (or `shopify-shop-domain`) header used to populate `WebhookMetadata#shop` is never part of the signed material. Any entity capable of obtaining a validly-signed webhook body for the app (e.g., a merchant who installs the app on their own store) can replay that exact body with an arbitrary `shop-domain` header, producing a request that passes HMAC validation while claiming to originate from a different (victim) shop.

### Finding Description
`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, verifiable_query.to_signable_string)` and compares it against the `hmac` field [1](#0-0) . For webhooks, `to_signable_string` is defined to return the raw JSON body only [2](#0-1) . The `shop` accessor, however, is read directly and unauthenticated from the `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler, then forwards `request.shop` unchanged as the tenant identifier in `WebhookMetadata`: [4](#0-3) . There is no check binding the claimed `shop` to anything covered by the HMAC (the app's api_secret_key is shared across all shops that install the app, not per-shop, so the same secret signs every installer's webhooks).

This breaks the intended identity binding: `shop header used by handler == shop that the signed bytes originated from`. In reality, the equality only holds for `signed_bytes == raw_body`; the `shop` header is out-of-band and attacker-controllable as long as the attacker can produce (or replay) a validly-HMAC'd body for the shared app secret. The docs explicitly instruct integrators to trust `data.shop` as "The shop domain of the webhook" [5](#0-4) , confirming this is the gem's documented/intended tenant-identification contract, and `WebhookMetadata#shop` is a plain, unauthenticated `String` field [6](#0-5) .

### Impact Explanation
Any merchant who installs the target app on their own store (a legitimate, unprivileged installer) receives genuine webhooks whose body is signed with the app's `api_secret_key`. Because the shop-domain header is excluded from the signed content, that merchant can capture a validly-signed webhook body and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. The HMAC check still passes (it only verifies the body bytes), and the handler receives `WebhookMetadata#shop` = victim shop. If the host application uses this `shop` value to look up per-tenant sessions/access tokens or to write/attribute data (which is exactly what the documented usage pattern in `docs/usage/webhooks.md` encourages — `shop_domain: data.shop`), this enables cross-tenant data confusion/write using the identity of an arbitrary shop the attacker does not control. This satisfies the "cross-tenant access" criterion for a Critical-impact finding, rooted entirely in this gem's `Registry`/`Request`/`HmacValidator` code, not in host-application misuse of an undocumented contract.

### Likelihood Explanation
Exploitation requires only that the attacker be an unprivileged party who has installed (or can install) the app on some shop they control — a normal, unprivileged capability for any public or unlisted Shopify app. No access token, `client_secret`, or privileged account is needed; the attacker only needs one legitimately-received webhook body/HMAC pair (trivially obtainable by triggering the subscribed event on their own store) and the ability to send an HTTP POST with a modified header to the app's webhook endpoint. This is a realistic, low-effort attack path.

### Recommendation
Bind the shop identity into the material that is actually verified. Options:
- Include the `shop-domain` header (and topic/webhook-id) in `to_signable_string`/HMAC computation so header tampering invalidates the signature (this would deviate from Shopify's actual webhook signing scheme, which only signs the body — so this isn't directly fixable purely client-side).
- More robustly, cross-validate `request.shop` against a fact that is authenticated, e.g., require the caller to look up an existing, previously-established Session/webhook subscription record for that `webhook_id` and confirm it was registered for the same shop before trusting `request.shop`, or validate the shop domain against the `X-Shopify-Shop-Domain` combined with a per-shop registered webhook `id` returned by Shopify at registration time (`get_webhook_id`) rather than trusting the header blindly.
- At minimum, explicitly document in `docs/usage/webhooks.md` that `data.shop` is not covered by the HMAC and must not be trusted as a tenant boundary without additional verification (e.g., matching it against the shop associated with the `webhook_id` via a stored registration lookup).

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker.myshopify.com`; trigger a subscribed webhook topic (e.g., `orders/create`) so Shopify sends a webhook with body `B` and header `x-shopify-hmac-sha256 = HMAC(api_secret_key, B)`.
2. Capture `B` and the HMAC value.
3. Replay a POST to the app's webhook endpoint with the same raw body `B`, the same (still-valid) `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` (`Request#to_signable_string`) and succeeds [7](#0-6) .
5. The handler is invoked with `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)` [8](#0-7) , causing the host application to act as though the event belongs to the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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
