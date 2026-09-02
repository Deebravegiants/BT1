### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are not covered by the HMAC, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC signature verified by `Registry.process` covers the payload bytes but not the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. Since the HMAC secret (`Context.api_secret_key`) is a single app-level secret shared by every shop that installs the app, any tenant can obtain a validly-signed `(raw_body, hmac)` pair from their own store and replay it to the app's public webhook endpoint with the `shop-domain` header rewritten to a victim shop, producing a request that passes signature validation while carrying an attacker-controlled tenant identity.

### Finding Description
`Request#to_signable_string` binds only the body to the signature: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated headers: [2](#0-1) [3](#0-2) 

`Registry.process` verifies the HMAC and then forwards the *unverified* header-derived `shop`/`topic` straight into the host app's handler as trusted metadata: [4](#0-3) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` against `verifiable_query.hmac`, i.e. it only checks that the body bytes were signed with the app secret — it says nothing about which shop the body was signed for: [5](#0-4) 

Because the same `api_secret_key` is used for every shop that installs the app (there is no per-shop key), a shop that legitimately installed the app can trigger any webhook event in its own store, capture the resulting `(raw_body, hmac)` pair, and then send an HTTP request directly to the app's public webhook endpoint with the same body/HMAC but a rewritten `shop-domain` (or `x-shopify-shop-domain`) header naming a different, victim shop. `Utils::HmacValidator.validate(request)` still succeeds because it only checks the body, and `WebhookMetadata.shop` — the value the host application uses to determine which tenant the event applies to — is the attacker-controlled header value. This breaks the intended identity binding: `shop (verified via HMAC) == shop (used to attribute/act on the event)`. In reality only `body (verified) == body`, while `shop (acted on) ≠ shop (this HMAC actually attests to)`.

This is the direct analog of the reported bug class: a field (`shop`) that is acted upon (used as tenant identity for downstream processing) is not covered by the integrity check (HMAC), allowing state confusion across trust boundaries — here, across shop tenants instead of across round-accounting states.

### Impact Explanation
This enables cross-tenant confusion/access: a low-privileged actor who is merely one tenant of a multi-tenant app can cause the app to process/attribute another shop's-looking webhook event using data of their own choosing (their own order/customer/product payload) while impersonating any target shop domain in the unauthenticated header, since `Registry.process` and `WebhookMetadata` never re-validate that the `shop` header matches the body's true origin. Any host application that keys per-tenant records or authorization decisions off `WebhookMetadata#shop` (exactly as documented in the gem's own webhook usage guide) can be tricked into writing/acting on data under the wrong shop, which meets the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitability only requires the attacker to run their own shop that has installed the target app (a normal, unprivileged action) and to be able to send an arbitrary HTTP POST to the app's public webhook route with custom headers — both trivially available to any internet user without needing `api_secret_key`, an access token, or any other privileged credential. No timing race or exotic condition is needed since headers are wholly detached from the HMAC.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signed content verified against the HMAC (or otherwise cryptographically bind them, e.g., by deriving/validating them from a per-request nonce tied to the signed body), and have `Registry.process` reject any request where header-derived identity fields cannot be proven to correspond to the signed body. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook-eligible event (e.g., updates a product), receiving a legitimate webhook POST from Shopify with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)`.
3. Attacker POSTs directly to the app's public webhook endpoint with the same body `B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC_SHA256(api_secret_key, B) == H` — this passes. [6](#0-5) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and the host app processes/attributes attacker-supplied data as belonging to the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
