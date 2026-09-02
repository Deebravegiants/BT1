### Title
Webhook shop/topic identity headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used downstream by `ShopifyAPI::Webhooks::Registry.process` are read directly from unauthenticated HTTP headers. The HMAC check therefore proves the *body* bytes are untampered, but never binds them to the *shop* the handler is told the event came from — breaking the identity binding `verified_bytes == bytes_that_determine_tenant`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version`, however, are parsed straight from the request headers, independent of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` only re-computes the signature over `to_signable_string` (i.e., the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` gates entirely on this HMAC check and then trusts `request.shop`/`request.topic` to build the metadata the host app's handler acts on: [4](#0-3) 

Because the app's `client_secret` (`Context.api_secret_key`) is the same secret used to sign webhooks for every shop that has installed the app, a low-privilege attacker (any merchant who installs the same app on their own store) can capture a legitimately-signed `(raw_body, hmac)` pair generated for their own shop, then replay it to the app's public webhook endpoint with the `shop-domain` (and/or `topic`/`webhook-id`) header changed to point at a different, victim shop. Since none of those headers are part of the signed bytes, `HmacValidator.validate` still succeeds, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-supplied) body came from the victim shop: [5](#0-4) 

The identity equality that should hold is: *the shop bound to the HMAC-verified bytes == the shop the handler is told the event is for*. Before the request: attacker's shop is bound to the raw body via the shared-secret HMAC. After the forged request: the handler receives `shop = victim_shop` for that same attacker-controlled, still-validly-signed body — the binding is broken.

### Impact Explanation
Any handler logic keyed on `WebhookMetadata#shop` (e.g., looking up the shop's stored offline access token to act on its behalf, or writing/deleting tenant-scoped data) can be tricked into operating on a shop the attacker does not own, using attacker-controlled body content. This is a cross-tenant access primitive that meets the Critical bar in the reward rules (cross-tenant access) since it lets one tenant's request/data spoof another tenant's webhook event and drive whatever access-token-bearing action the host application performs in its handler.

### Likelihood Explanation
Exploitation requires only: (1) the attacker installs the app on a shop they control (a normal, unprivileged action available to any merchant), (2) they receive one real webhook to capture a valid `(body, hmac)` pair, and (3) they POST that pair to the app's public webhook endpoint with a modified `shop-domain`/`topic` header. No access token, `client_secret`, or privileged account is needed — only the ability to install the app once and send an HTTP request, which is exactly the unprivileged-internet-user threat model in scope.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (or otherwise cryptographically bind them to the verified payload) so that `HmacValidator.validate` fails if any of these identity-determining headers are altered relative to what Shopify actually signed. At minimum, document that host applications must not trust `WebhookMetadata#shop`/`topic` unless these fields are independently corroborated (e.g., against the session/shop the webhook subscription was registered for).

### Proof of Concept
1. App developer's `client_secret` is `S`. Attacker installs the app on `attacker.myshopify.com` and receives a legitimate webhook: `raw_body = '{"id":1}'`, headers include `x-shopify-hmac-sha256 = Base64(HMAC-SHA256(S, raw_body))`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the new headers; `Utils::HmacValidator.validate(request)` recomputes the HMAC over `raw_body` only (`to_signable_string` returns `@raw_body`) — [1](#0-0)  — which still matches, so `Registry.process` dispatches the handler with `shop: "victim.myshopify.com"` and the attacker-authored body — [4](#0-3) .
4. Any handler that trusts `metadata.shop` to select the tenant context/access token now operates on `victim.myshopify.com` using attacker-controlled data.

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
