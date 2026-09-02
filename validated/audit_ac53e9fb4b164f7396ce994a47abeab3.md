### Title
Webhook shop-domain spoofing due to `shop` header not covered by HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` only verifies the HMAC over the raw request body. The `shop` (and `topic`/`webhook_id`/`api_version`) values are read straight from HTTP headers that are **not** part of the signed payload. Since a single app's `api_secret_key` is shared across every shop that installs the app, any tenant can generate a genuinely-valid HMAC for an attacker-chosen body (by triggering a real webhook on their own store) and then replay that body with a forged `shop-domain` header pointing at a victim shop. The handler receives `WebhookMetadata` claiming the payload belongs to the victim shop, breaking the binding between "shop whose secret produced this signature" and "shop the application will act on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly from HTTP headers and are never included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` (via `validate_signature`) computes the signature purely from `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header — it never incorporates `shop`: [3](#0-2) 

`Registry.process` trusts `request.shop` for tenant identification as soon as the body HMAC checks out, and hands it straight to the app's handler: [4](#0-3) 

Because `Context.api_secret_key` is one shared secret for the whole app (not per-shop), any merchant who installs the app can legitimately trigger a webhook with a body they control (e.g., by creating an order/product in their own store) and obtain a body+HMAC pair signed with the app's real secret. They can then replay that exact body/HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes because it never checks `shop`, and `Registry.process` forwards `shop: request.shop` (the attacker-supplied victim domain) to the handler as if Shopify itself asserted that shop.

### Impact Explanation
This breaks the equality `shop that produced the valid signature == shop the application attributes and acts on`. Any application logic that uses the webhook's `shop` field to look up/update per-tenant state (the documented, intended usage per `WebhookMetadata`) can be tricked into writing or acting on attacker-controlled body data under a victim shop's identity — a cross-tenant integrity violation reachable by any unprivileged merchant who has installed the app on their own store.

### Likelihood Explanation
Any shop can install the app (the normal, unprivileged flow), trigger real events in their own store, and use standard tooling to replay the resulting webhook HTTP request while modifying only the `shop-domain` header. No secret material is needed. The library's own test suite confirms only the body-HMAC pair is validated and that `shop` is read verbatim from the header, with no cross-check against it.

### Recommendation
Bind the header-derived identity fields to the signature verification, e.g. include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string (or otherwise cryptographically bind them), or require the host application to independently corroborate the claimed `shop` (e.g., against an active, previously-registered webhook/session for that shop and topic) before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers an event (e.g., `orders/create`) with attacker-chosen order content, causing Shopify to POST a webhook to the app with a body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker intercepts this outgoing request (they control the receiving endpoint or a proxy in front of it) and re-sends it to the app's webhook endpoint with the same body `B` and same valid `hmac` header, but with `x-shopify-shop-domain` changed to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because only `B` is checked.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, causing the app to process/store attacker data under the victim's tenant.

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
