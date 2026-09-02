### Title
Webhook `shop` identity is not covered by the HMAC signature yet is trusted by `Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` passes, then forwards `request.shop` (an unauthenticated HTTP header) to the app's handler as the tenant identifier inside `WebhookMetadata`. The HMAC signature that is actually verified only covers the raw request body, not the `shop-domain` header, so the "verified" webhook and the `shop` value the handler acts on are two different things that are never checked to be equal.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from a caller-controlled header, entirely independent of the signature: [2](#0-1) 

`Registry.process` validates the HMAC of the request (i.e., of the body against the shared `api_secret_key`) and, once that single check passes, hands `request.shop` directly to the registered handler as the authoritative tenant identity, with no binding between the verified body and the claimed shop: [3](#0-2) 

The identity equality that the library implicitly promises to callers is:
`hmac_valid(body, api_secret_key) == true` implies `shop == body.origin_shop`

But the actual guarantee provided is only:
`hmac_valid(body, api_secret_key) == true`, with `shop` taken from an independent, unsigned header.

Because every shop installed on a given app shares the same `api_secret_key`, any body+HMAC pair that is valid for one tenant (e.g., one obtained from the attacker's own store, which they legitimately control and can trigger real webhook deliveries from) remains a byte-for-byte valid HMAC pair no matter what `shop-domain` header accompanies it. An attacker who operates their own shop installation of the target app can capture one legitimately signed webhook body/HMAC pair, then replay it to the same public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop. `Utils::HmacValidator.validate` still returns `true` (it only recomputes the signature over `@raw_body`), and `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: <victim-shop>, body: <attacker-controlled-payload>, ...)`.

### Impact Explanation
Any host application that relies on `WebhookMetadata#shop` (as returned by this gem's own `Registry.process` method, without any documented caveat that it is unauthenticated) to select or scope the tenant record to create/update/delete will process attacker-supplied data under a victim shop's identity. This is a cross-tenant data-integrity/access issue: the confidentiality/integrity boundary between tenants of the same app is broken using only a legitimate account on the attacker's own shop, no access token, secret, or privileged credential of the victim is required.

### Likelihood Explanation
The primitives required are trivial for any unprivileged internet user who can install the target app on their own (attacker-owned) shop: (1) trigger any webhook-eligible action to obtain one valid raw-body/HMAC pair, (2) replay it to the app's public webhook endpoint with a modified `shop-domain` header. No secret material, TLS interception, or social engineering is needed; the request is fully self-contained and reusable at will.

### Recommendation
Bind the header-derived `shop` (and other headers the handler is expected to trust, such as `topic`/`api-version`) into the signed material, or otherwise cryptographically tie the claimed shop to the verified payload, e.g. by including the relevant headers in `to_signable_string` (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop` in its signable string) or by requiring the host application to independently confirm `request.shop` against a shop it already trusts (e.g. the session/store the webhook subscription was registered for) before acting on the payload. At minimum, document prominently that `WebhookMetadata#shop` is not covered by the HMAC check and must not be used as a sole tenant-scoping key.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and configures a webhook subscription (e.g. `orders/create`) that is delivered to the app's public webhook endpoint.
2. Attacker triggers the event and captures the raw POST body plus the `X-Shopify-Hmac-Sha256` header Shopify sent - this pair is valid because it is signed with the app's shared `api_secret_key`.
3. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`@raw_body` only) and finds it matches - validation succeeds.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)`, causing the host application to process attacker-controlled data under the victim shop's identity. [4](#0-3) [3](#0-2)

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
