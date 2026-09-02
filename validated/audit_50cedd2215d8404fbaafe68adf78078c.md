## Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC signature over the raw request body only, while the shop domain, topic, and webhook id used by the application's webhook handler are read directly from unauthenticated HTTP headers. This breaks the identity binding between "bytes verified by the HMAC" and "the shop/topic the payload is processed as," letting an attacker who controls (or replays) any validly-signed webhook body reassign it to an arbitrary target shop or topic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers that are never part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)` and, once that passes, immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to build `WebhookMetadata` and dispatch it to the registered handler — with no cross-check that the signed body actually corresponds to the claimed shop or topic: [3](#0-2) 

`HmacValidator.validate` only proves `computed_signature(to_signable_string, api_secret_key) == received_signature`; it says nothing about the `shop-domain` or `topic` headers: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`verified(raw_body)` (what the HMAC actually authenticates) ≠ `acted_upon(shop, topic, webhook_id)` (what the handler uses to decide which tenant/topic the event belongs to).

Since every shop of a given app shares the same `api_secret_key` for webhook HMAC computation, a validly-signed `(raw_body, hmac)` pair delivered to the app for one shop (e.g., an attacker's own store, which they fully control and can trigger webhooks on) can be replayed to the same endpoint with the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header rewritten to name a different, victim shop. `HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim's shop with attacker-controlled body content.

### Impact Explanation
Any host application whose webhook handlers key off `WebhookMetadata#shop` (e.g., to look up/act on that shop's stored access token, update tenant records, or drive business logic per-tenant) can be tricked into performing actions attributed to, or affecting, a shop the attacker does not control. This is a cross-tenant boundary violation caused entirely by this gem's webhook verification not binding the authenticated bytes to the shop/topic claims it exposes to callers — matching the Critical "cross-tenant access" impact category, since the attacker forges data attributed to another merchant's tenant using only their own legitimate webhook traffic and no leaked secrets.

### Likelihood Explanation
Exploitation requires only that the attacker operate their own Shopify store installed with the target app (a normal, unprivileged capability), trigger any webhook topic on their own shop to obtain a valid `(raw_body, hmac)` pair, and then POST that captured body/HMAC to the app's webhook endpoint with a modified shop-domain (and optionally topic) header. No access to `api_secret_key`, tokens, or the target shop is needed, and the gem provides no built-in defense (e.g., no shop allowlist enforcement or body/header binding) — likelihood is high for apps that trust `WebhookMetadata#shop`/`#topic` as attacker-uncontrollable.

### Recommendation
Bind the shop/topic/webhook-id headers into the HMAC-verified signable string (or otherwise cryptographically tie them to the body), so that spoofing any of these header values invalidates the signature. At minimum, `Utils::HmacValidator`/`Webhooks::Request` should incorporate `shop`, `topic`, and `webhook_id` into `to_signable_string`, or `Registry.process` should cross-validate the shop/topic against the parsed body content (where Shopify includes it) before dispatching to handlers.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and lets Shopify send a legitimate webhook (any topic) to the app's endpoint, capturing the raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify using the app's shared `api_secret_key`).
2. Attacker replays a POST to the same webhook endpoint with:
   - Body: `B`
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid for `B`)
   - Header `X-Shopify-Shop-Domain: victim.myshopify.com` (rewritten)
3. `Utils::HmacValidator.validate(request)` succeeds because it only recomputes the HMAC over `B`, per `lib/shopify_api/utils/hmac_validator.rb:26-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata` with `shop: "victim.myshopify.com"` and dispatches attacker-controlled `body` to the handler, which the host application will treat as an authentic event for the victim's tenant.

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
