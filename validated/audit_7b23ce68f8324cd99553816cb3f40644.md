### Title
Webhook `shop` and `topic` identity fields are unauthenticated (not covered by HMAC signature) — cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature (`to_signable_string`) solely over the raw request body [1](#0-0) , while the `shop` and `topic` identity fields used downstream to route and attribute the payload are read directly from unsigned HTTP headers [2](#0-1) . `Registry.process` accepts any request whose body-HMAC validates and then constructs `WebhookMetadata` using `request.shop` and `request.topic` taken from those unsigned headers, handing them to the host app's handler as trusted tenant identity [3](#0-2) . The identity binding broken is: `HMAC-signed bytes (body only) == identity bytes acted upon (shop header)`, which the gem's own `HmacValidator.validate` never checks [4](#0-3) .

### Finding Description
`HmacValidator.validate` verifies only that `HMAC(api_secret_key, to_signable_string)` matches the received signature [5](#0-4) . For `Webhooks::Request`, `to_signable_string` returns `@raw_body` exclusively [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all parsed straight from HTTP headers with no participation in the signed payload [6](#0-5) .

`Registry.process` uses exactly this unauthenticated `shop`/`topic` to build the `WebhookMetadata` struct passed to the app's handler as ground truth tenant/topic identity:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [3](#0-2) 

Critically, the `api_secret_key` used to compute the HMAC is the **app-wide** client secret — identical for every shop that has installed the app — not a per-shop secret [7](#0-6) . This means any merchant who has legitimately installed the app (an "unprivileged" party relative to any other tenant) can trigger a real, correctly-signed webhook delivery for their own shop (e.g., by creating an order), capture the `raw_body` + genuine `x-shopify-hmac-sha256` value from that delivery, and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain and/or the `x-shopify-topic` header changed. Because the HMAC check only covers `@raw_body`, `HmacValidator.validate` still returns `true`, and `Registry.process` forwards `WebhookMetadata` with the attacker-chosen `shop` field to the handler as if Shopify itself attested that the body originated from the victim tenant.

This breaks exactly the identity-binding invariant the analog rules describe: "a field acted on (`shop`) but not covered by the HMAC." The gem does not document (nor could it, since it does not control headers) that `request.shop`/`request.topic` need independent verification beyond what `HmacValidator.validate` already performs; a caller following the gem's own `Registry.process` API is guided directly into trusting unauthenticated fields.

### Impact Explanation
This enables cross-tenant data injection: an attacker who owns/controls their own installed shop can forge webhook events "from" any other shop known to have installed the app (shop domains are commonly guessable/enumerable), causing the host application's webhook handler to process attacker-supplied body content (limited to shapes the attacker can produce from their own store's events) under a victim shop's identity. Depending on what the handler does with `data.shop` (e.g., updating victim-shop-scoped records, triggering side effects keyed by shop), this is a cross-tenant access vulnerability that meets the Critical impact bar ("cross-tenant access").

### Likelihood Explanation
Requires the attacker to be a legitimate (but unprivileged, non-victim) merchant who has installed the target app — no possession of the app's `client_secret` or any access token is required, since the attacker legitimately receives a genuinely-signed webhook body from Shopify for their own shop and only needs to modify unsigned HTTP headers on replay, which any internet-capable client can do. The victim shop domain is typically public (`*.myshopify.com`, often equal to the storefront domain). This is a realistic, moderately likely scenario given normal app usage.

### Recommendation
Bind `shop` (and ideally `topic`) into the signed payload check, e.g. by having `HmacValidator`/`Webhooks::Request` verify the header-derived `shop` against the shop that the raw body's contents actually belong to (Shopify's resource payloads include shop-scoped identifiers), or by requiring host apps to cross-check `request.shop` against a known/expected shop before trusting it. At minimum, document prominently that `WebhookMetadata#shop` is not covered by `HmacValidator.validate` and must not be treated as authenticated without additional verification (e.g., matching against the currently active session's shop, or enforcing per-shop webhook secrets if Shopify supports them for the account).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Attacker triggers a real webhook (e.g. `orders/create`) and captures the raw POST: `raw_body` and header `x-shopify-hmac-sha256: <valid_hmac>` (computed by Shopify with the app's shared `client_secret`).
3. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` header to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes and compares against `@raw_body` [1](#0-0)  — validation succeeds because the body/HMAC pair is genuinely valid.
5. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"` [8](#0-7) , even though the payload actually originated from the attacker's own store.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
