### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing on replayed webhooks - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop` attribute that is handed to the app's webhook handler is read from an unauthenticated header. The identity binding the gem is supposed to enforce — "the `shop` a webhook is attributed to == the tenant that Shopify actually signed this delivery for" — does not hold, because `shop` is never part of the signed bytes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic tie to the body or the HMAC: [2](#0-1) 

`Registry.process` validates only that `hmac` matches `to_signable_string` (i.e., the body), then immediately forwards the unauthenticated `request.shop` value into `WebhookMetadata`, which is delivered to the app's handler as the trusted tenant identifier: [3](#0-2) [4](#0-3) 

Because the app's `api_secret_key` is shared across every shop that installs the app (it is not per-tenant), a valid `(body, hmac)` pair obtained from *any* installation of the app (including one an attacker legitimately installs on their own store) remains a valid signature for that exact body no matter which shop it is later claimed to be from. An attacker who:
1. Installs the target app on their own shop (fully legitimate, unprivileged action), and
2. Captures one real webhook delivery (raw body + `x-shopify-hmac-sha256` header) that Shopify sends them,

can replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at the header), and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop, while `body` is fully attacker-controlled (it is whatever content the attacker's own store produced, and can be edited further as long as `hmac` is not desired to match — but the attacker can generate arbitrary valid-body/HMAC pairs on demand simply by triggering webhook-eligible events on their own store, e.g. editing an order note, creating a product, etc., and observing the corresponding signed body).

This breaks the equality the library is expected to guarantee:
`shop authenticated by the app's secret == shop attributed to the delivered data`, which becomes `shop that actually signed the body != shop label the handler receives`.

### Impact Explanation
Any app whose webhook handler uses `data.shop` to key persistence, authorization, or to select which merchant's access token/session to act on will process attacker-supplied webhook content under a victim shop's identity. Depending on handler logic this enables cross-tenant data corruption (e.g., writing attacker content into records keyed by the victim's shop) or triggering merchant-scoped actions attributed to the wrong tenant — a cross-tenant integrity/confidentiality violation reachable by any unprivileged internet user who can install the app once on a shop they control.

### Likelihood Explanation
High. No credentials, secrets, or privileged access are required beyond a normal app installation that is open to any merchant (the standard install flow for Shopify apps). Capturing a self-triggered webhook delivery and replaying it with a modified header is trivial and requires no interaction with the app's `api_secret_key`.

### Recommendation
Bind the `shop` attribution to the signed payload rather than trusting the header in isolation:
- Include the `shop` domain (and ideally `topic`/`webhook_id`) inside the signable string used for HMAC verification, or
- Independently verify that the shop domain in the header corresponds to a shop the app has an active, previously-established session/installation for, and reject/flag any mismatch between the webhook's declared shop and any shop-scoped identifiers embedded in the JSON body (e.g., resource IDs known to belong to a different tenant), or
- At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and that host applications must independently verify shop ownership before using it for authorization decisions.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` (normal, unprivileged installation).
2. Attacker performs an action that triggers a subscribed webhook topic (e.g. `orders/create`) and captures the raw POST body `B` and header `x-shopify-hmac-sha256: H` sent by Shopify to the app's webhook endpoint.
3. Attacker resends the exact same request to the app's public webhook endpoint, but replaces the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`, keeping body `B` and `hmac H` unchanged:
   ```
   POST /webhooks/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: H
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: B
   ```
4. `HmacValidator.validate` succeeds because it only checks `H` against `B` [5](#0-4) 
5. `Registry.process` calls the registered handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, i.e., attacker-controlled data processed as belonging to `victim-shop`. [3](#0-2)

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
