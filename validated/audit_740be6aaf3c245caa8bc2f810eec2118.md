### Title
Webhook `shop-domain` (and `topic`) headers are not covered by the HMAC signature, allowing cross-tenant webhook forgery via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator` verifies the HMAC exclusively against that body. The `shop` (and `topic`) values that `ShopifyAPI::Webhooks::Registry.process` uses to select the handler and populate `WebhookMetadata` come from unauthenticated HTTP headers that are never bound into the signed bytes.

### Finding Description
`Request#hmac`/`#to_signable_string` sign/verify only `@raw_body`: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the secret — it never mixes in `shop`, `topic`, `webhook_id`, or `api_version`: [3](#0-2) 

`Registry.process` then trusts `request.shop` and `request.topic` (taken straight from headers) once the body-only HMAC passes, and dispatches to the handler with that unauthenticated shop value: [4](#0-3) 

Because the `shop-domain` header is never covered by the signature, any request bearing a **previously-observed, validly-signed body** (i.e. one the attacker legitimately received for their own shop from Shopify) can be replayed to the same public webhook endpoint with the `x-shopify-shop-domain` header swapped to a victim shop. `HmacValidator.validate` will still pass because it only re-derives the HMAC from the untouched body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop: [4](#0-3) 

This breaks the equality the host application relies on: `shop` used by the handler to key tenant data == `shop` cryptographically bound to the signed payload. In reality, `shop` (header) ≠ any value covered by the HMAC.

### Impact Explanation
Many webhook topics carry generic or empty bodies (e.g. `app/uninstalled`, `shop/redact` compliance webhooks send `{}` or fixed-shape JSON that doesn't itself encode the shop). An attacker who installs the app on their own (unprivileged, self-controlled) development store can capture one legitimately-signed webhook delivery, then replay that exact body+HMAC to the app's public webhook URL while substituting the victim's shop domain in the header. Any host application that trusts `WebhookMetadata#shop` to select the tenant record to mutate (e.g., mark uninstalled, purge/redact data, disable a subscription) can be tricked into acting on the wrong tenant — a cross-tenant data-integrity impact reachable by an unauthenticated attacker who never possessed the victim's or app's secret.

### Likelihood Explanation
Requires the attacker to (1) install the app on any shop they control (an unprivileged action available to anyone), (2) trigger/receive one webhook with a body that is topic-generic (several mandatory/compliance topics qualify), and (3) send a forged POST to the app's public webhook endpoint with the same body/HMAC but a different `shop-domain` header. No secret material, TLS interception, or privileged access is required — only observation of one's own legitimately received webhook traffic.

### Recommendation
Bind the security-relevant headers (`shop`, `topic`, `webhook-id`, `api-version`) into the signed material verified by `HmacValidator`, or otherwise cryptographically tie the `shop-domain` header to the payload (e.g., verify it out-of-band against the session/shop the app expects for that webhook subscription) before trusting `WebhookMetadata#shop` for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives a real, Shopify-signed webhook, e.g. `app/uninstalled` with body `{}` and header `x-shopify-hmac-sha256: <validHMAC>` computed by Shopify over `{}`.
2. Attacker replays the captured request to the same public webhook endpoint, keeping body `{}` and the same `x-shopify-hmac-sha256`, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`{}`) using `Context.api_secret_key`; it matches because the body is unchanged: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", ...)`, causing the app to process an uninstall/redact/etc. action against `victim.myshopify.com` even though Shopify never sent this webhook for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
