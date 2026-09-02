Confirmed: the HMAC signature for webhooks is computed only over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` value used for tenant identification comes from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed material.### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` value it hands to the app's `WebhookHandler` is read directly, unauthenticated, from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` HTTP header. Because `HmacValidator.validate` only checks `body + Context.api_secret_key` against the signature, and the app's `api_secret_key` is a single value shared by every shop that installs the app, any user who installs the app on a shop they control can capture one of their own legitimately-signed webhook deliveries and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. The HMAC still validates (body unchanged), but the handler is invoked believing the (attacker-controlled) payload originated from the victim shop.

### Finding Description
The relevant binding that should hold is:

`hmac == HMAC(api_secret_key, shop || body)`

but the implementation actually enforces only:

`hmac == HMAC(api_secret_key, body)`

Evidence:
- `to_signable_string` returns solely the raw body: [1](#0-0) 
- `shop` is read straight from the (attacker-controllable, unsigned) headers, with no cross-check against anything covered by the HMAC: [2](#0-1) 
- `HmacValidator.validate`/`validate_signature` verifies the signature purely as a function of `to_signable_string` (i.e., the body) and the shared `api_secret_key`: [3](#0-2) 
- `Registry.process` validates the HMAC and then dispatches the handler using `request.shop`, which is the unauthenticated header value: [4](#0-3) 
- The dispatched `WebhookMetadata.shop` field is what host apps use to select per-tenant data/records to act on: [5](#0-4) 

Because `api_secret_key` (the app's `client_secret`) is global to the app, not per-shop, any legitimate merchant/attacker who installs the app on their own store receives real webhook deliveries whose HMAC is computed with that same shared secret. The attacker can capture the `(raw_body, hmac)` pair from a webhook delivered to their own shop, then POST that identical body/HMAC pair to the app's webhook endpoint again while substituting a victim shop's domain in the `shop-domain` header. `HmacValidator.validate` still succeeds because it never inspects `shop`, so the forged request is accepted as authentic and routed to the handler tagged with the victim's shop identity, while the body content is entirely attacker-controlled (from their own store).

This is the direct analog of the external report's root cause: a value acted upon by downstream logic (`amountOut` for the external report; `shop` here) is not covered by the same integrity check (`takeFee`'s fee deduction there; the HMAC signature here) that the caller relies on to trust the result.

### Impact Explanation
This breaks the tenant-authentication boundary the gem is meant to provide: `Registry.process` is documented and used by host apps as their sole authenticity check for "this webhook body really came from Shopify for shop X." An attacker who is a legitimate (even free/trial) merchant of the app can forge webhook events "from" any other tenant shop, with a body of their choosing, and have it accepted as authentic. Depending on how the host app's `WebhookHandler#handle` implementation uses `data.shop` (e.g., updating billing state, redacting/creating data, revoking access, marking uninstall, triggering GDPR compliance flows, updating stored per-shop settings), this enables cross-tenant data corruption or the triggering of privileged actions against another merchant's account — a cross-tenant impact within the meaning of the rules ("cross-tenant access").

### Likelihood Explanation
Likelihood is High for any host app that trusts `WebhookMetadata#shop` for cross-tenant identification (the intended and documented use), which is essentially all downstream users of `ShopifyAPI::Webhooks::Registry`/`WebhookHandler`. The only prerequisite is that the attacker be able to install the target app on a shop they control (or otherwise receive at least one legitimate webhook delivery), which is a routine, unprivileged action available to any merchant/developer account — not a leaked credential, TLS interception, or social engineering.

### Recommendation
Bind the tenant identity into the signed material that `HmacValidator` verifies, e.g., include `shop` (and/or `topic`/`webhook_id`) in `Webhooks::Request#to_signable_string` rather than only the raw body, or perform a secondary comparison that ties the HMAC-verified body to the shop the webhook claims to be from (for example, verifying the shop domain against the domain expected for the resource IDs embedded in the body, or requiring apps to look up an existing installed session for the claimed shop before trusting the payload). At minimum, document prominently that `WebhookMetadata#shop` is not itself authenticated by the HMAC and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a shop they control), which is a normal, unprivileged flow.
2. Shopify delivers a real webhook (e.g. `orders/create`) to the app's webhook endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — the same `api_secret_key` used for every shop on this app installation.
3. Attacker captures `(B, H)` (e.g., from their own server logs, since it was delivered to their own endpoint).
4. Attacker crafts a new HTTP POST to the same webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (attacker-modified)
5. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and finds it equals `H` — validation passes [6](#0-5) .
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [7](#0-6) , even though `B` originated from the attacker's own shop, not the victim's.

Note: I could not verify from the indexed files exactly how `Context.api_secret_key` is scoped in multi-tenant deployments (e.g., whether some host apps configure per-shop secrets outside this gem); this analysis assumes the single global `Context.api_secret_key` configuration shown in `lib/shopify_api/context.rb`, which is the gem's documented/standard setup.

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
