## Title
Webhook shop-domain identity spoofing via HMAC that only covers the body, not the shop header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw body only, while the shop identity used to route/process the webhook (`request.shop`) comes from the `x-shopify-shop-domain` header, which is never covered by the HMAC. `Registry.process` verifies only `Utils::HmacValidator.validate(request)` and then dispatches to the handler using the unauthenticated `shop` value, breaking the binding "shop that produced a validly-signed payload" == "shop the handler believes sent it."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled straight from HTTP headers and are never part of the signed material: [2](#0-1) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against the received signature — for a `Request`, this is `HMAC(secret, raw_body)` only: [3](#0-2) 

`Registry.process` performs no additional check on `request.shop`; it validates the HMAC, then immediately builds `WebhookMetadata` (used by the app's business logic) directly from the unauthenticated `shop` header: [4](#0-3) 

Because the webhook signing secret (`api_secret_key`) is shared by the app across *all* shops that install it (it is not shop-specific), any merchant who installs the app can trigger a webhook to their own store (e.g. `orders/create`) and legitimately receive a `(raw_body, hmac)` pair that is valid under this shared secret. That attacker can then send a forged HTTP request directly to the app's public webhook endpoint using that captured, genuinely-valid `(raw_body, hmac)` pair, but with the `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) headers replaced with a victim shop's domain. `HmacValidator.validate` only checks that the HMAC matches the body — it has no way of knowing whether the body came from the shop the header claims — so the forged request passes validation, and the app's webhook handler executes as if the payload had been sent by the victim shop.

This is a direct analog of the reported bug class: a field acted upon (`shop`) is not covered by the integrity check (HMAC), so the identity used for dispatch is decoupled from the identity that was actually authenticated.

### Impact Explanation
This breaks the tenant boundary that webhook processing is supposed to enforce: an unprivileged merchant installing the app can inject arbitrary attacker-controlled webhook bodies (of any topic they can normally receive) that the app will process as belonging to a different, victim shop. Depending on how the app's webhook handlers key data (which is the expected/documented usage pattern — handlers key off `WebhookMetadata#shop`), this enables cross-tenant data corruption/injection, e.g., spoofed `app/uninstalled` to wipe another shop's app data, or spoofed `orders/create`/`customers/*` payloads attributed to a shop that never sent them. This meets the "cross-tenant access" high/critical impact bar since it crosses the app's tenant isolation without needing the victim's or the app's access token, and without TLS interception (the attacker only needs a legitimately-signed body from their own shop, which they can self-generate).

### Likelihood Explanation
Likelihood is meaningful: any user who can install the app on a shop (even a free trial/dev store) can trigger self-owned webhooks to harvest a valid `(body, hmac)` pair, and can then send a crafted direct HTTP request to the app's public webhook URL with a different `shop-domain` header. No secret material, no interception, and no elevated privilege is required — only the ability to install the app on a shop the attacker controls, which is the baseline "unprivileged internet user" capability for a public Shopify app.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api-version) as part of the signed/verified material, or otherwise cryptographically/structurally bind the header-provided `shop` to the payload before dispatching to handlers. At minimum, gems/host apps should be told to double-check `shop` against a shop known to have installed the app (e.g., verify shop is a known, currently-installed tenant) before trusting `WebhookMetadata#shop`; but the more robust library-level fix is to not treat `shop`, `topic`, `webhook_id`, and `api_version` as trusted just because the (unrelated) body HMAC matched — e.g., have `to_signable_string` incorporate a canonical representation of shop/topic bound to the body, matching how the shop-scoped webhook signature works upstream, or reject/flag when the shop header cannot be corroborated against an active session/install record before invoking handlers.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Attacker performs an action that triggers a legitimate webhook (e.g., `orders/create`) to the app's registered webhook endpoint. Shopify sends:
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body under shared api_secret_key>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - body: attacker-controlled JSON payload (attacker can shape order fields as they can control what they order).
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value (they own the receiving endpoint or can capture it in transit to their own server without any interception of others' traffic).
4. Attacker sends a new HTTP POST directly to the app's public webhook URL with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes `HMAC(secret, raw_body)` and matches — validation succeeds: [5](#0-4) 
6. The handler is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, even though the payload originated from the attacker's own store — cross-tenant identity spoofing achieved without any credential belonging to the victim or the app.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
