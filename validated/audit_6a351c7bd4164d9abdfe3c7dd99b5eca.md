### Title
Webhook shop-domain identity is trusted without HMAC coverage, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then forwards these unauthenticated header values straight to the app's webhook handler as if they were verified, breaking the binding between "the entity whose secret produced this valid HMAC" and "the shop this event is attributed to."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from request headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` verifies only the HMAC (which covers the body, not the headers) and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` to build `WebhookMetadata` passed to the handler: [3](#0-2) 

Because a single app's `client_secret` is shared across every shop that installs it, any merchant who installs the app can legitimately receive a real, correctly-HMAC-signed webhook body for their own store, then replay that same `(body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header to point at a different, victim shop. `Utils::HmacValidator.validate` only recomputes/compares the HMAC of the body — identical for the same body regardless of which header values accompany it — so the request passes validation: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but does not:
`shop value used by the app's handler == shop that the HMAC-secret holder actually authenticated for this body`.
Before the attack: body B was authenticated for shop A (the attacker's own tenant). After the attack: the same authenticated body B is delivered and processed by the handler as belonging to shop V (an arbitrary/victim shop domain chosen by the attacker), because the header carrying `shop` was never part of the signed material.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate but low-privilege install of the app (no admin API credentials or leaked secrets required — just normal merchant use of a free trial/dev store) can inject events attributed to another shop into the app's webhook processing pipeline, or repeatedly re-deliver/relabel their own webhook to different shop identifiers. Any app logic that keys off `WebhookMetadata#shop` (e.g., to look up per-shop state, invalidate/uninstall accounts, trigger tenant-scoped side effects, or attribute billing/inventory events) can be manipulated to act on the wrong tenant — a cross-tenant access condition.

### Likelihood Explanation
Likelihood is moderate: the attacker needs to install the target app on any shop they control (an ordinary, low-barrier action, not a credential leak) to obtain a genuinely-signed `(body, hmac)` pair, then replay it with a forged shop-domain header to the app's public webhook endpoint. No secrets, tokens, or privileged access are required — only the ability to relay HTTP requests with custom headers, which any unprivileged internet user can do once they hold one valid signed payload.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable material, or otherwise cryptographically bind them to the body (e.g., have `to_signable_string` concatenate body plus these header values before hashing). Additionally, apps should be encouraged/required to cross-check the header `shop` against a shop that is actually known to have installed the app before trusting `WebhookMetadata#shop` for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, receiving a legitimate webhook: body `{"id":123}` with header `X-Shopify-Hmac-Sha256: <valid HMAC of body using the app's shared client_secret>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — [1](#0-0)  — and the check passes because the body is unchanged.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: {"id":123}, ...)` — [5](#0-4)  — and processes the attacker's event as if it originated from the victim shop.

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
