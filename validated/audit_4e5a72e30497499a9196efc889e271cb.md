### Title
Webhook shop/topic identity spoofing via HMAC that only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw body, while the `shop`, `topic`, `webhook-id`, and `api-version` values that are handed to the host application's handler come from unauthenticated HTTP headers. Because `Context.api_secret_key` is a single, app-wide secret shared across every shop that installs the app, any attacker who can obtain one validly-signed webhook (e.g. by installing the app on a shop they control) can replay that same signed body while forging the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to point at a victim shop. The HMAC check still passes, and the host app's handler is invoked believing the data belongs to the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `hmac` is computed by decoding the `hmac-sha256` header, independent of any other header: [2](#0-1) 

`Registry.process` uses this HMAC as the sole gate before dispatching to the handler with header-derived, unauthenticated identity fields: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it against the received HMAC: [4](#0-3) 

The identity binding that should hold is:
`shop header value used by the handler == shop that the HMAC-signed bytes were actually generated for`

But the HMAC only binds `raw_body`, not `shop`, `topic`, `webhook_id`, or `api_version`:
`bytes verified (raw_body) != bytes/headers acted on (shop, topic, webhook_id, api_version)`

Because `api_secret_key` is one shared secret for the whole app (not scoped per shop), any shop that installs the app can generate a validly HMAC-signed webhook body. That body/HMAC pair can then be replayed with a different `x-shopify-shop-domain` (and/or `x-shopify-topic`) header pointing at a different, victim shop. `Registry.process` still calls `HmacValidator.validate`, which passes since it never inspects the shop or topic headers, and then dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` to the app's handler using the forged values: [5](#0-4) 

The library's own documentation instructs handler authors to trust `data.shop` as "The shop domain of the webhook" without any indication that this value is unauthenticated: [6](#0-5) 

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an attacker who is a legitimate merchant of the app (i.e., installs the app on their own store to obtain a validly-signed webhook) can make the host application believe that attacker-controlled webhook data belongs to an arbitrary victim shop. Since `Registry.process` is the gem's blessed authentication primitive for webhooks, and host apps are documented to treat `data.shop`/`data.topic` as authenticated, this is a cross-tenant identity-confusion vulnerability rooted entirely in this gem's verification logic (HMAC not covering the shop/topic identity fields it hands to the handler).

### Likelihood Explanation
Likelihood is high for any attacker capable of installing the target app on a store they control (which is generally trivial for any public/embedded Shopify app, since app installation itself requires no special privilege beyond having a Shopify store). Once installed, the attacker receives real Shopify-signed webhooks for their own shop and can freely replay/forge the shop-domain (and topic) headers, because these are never covered by the signature.

### Recommendation
Bind the shop (and topic) identity into what is cryptographically verified, not just the body:
- Include `shop`, `topic`, `webhook_id`, and `api_version` in the string that is HMAC-verified (or otherwise validate them against Shopify's registered per-shop expectations before the record is trusted), similar to how OAuth's `AuthQuery#to_signable_string` binds all relevant fields.
- Alternatively, require host applications to independently confirm that `data.shop` corresponds to a shop that this app has installed/knows about (e.g., cross-check against stored sessions) before trusting the payload — and update the gem's documentation to explicitly call out that `shop`/`topic` are not part of the HMAC signature and must be independently verified by the consuming app.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a real webhook delivery, e.g. for `orders/create`, with headers:
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: <valid HMAC of body B computed with the app's shared api_secret_key>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - body `B` (attacker fully controls the order contents on their own shop).
2. Attacker replays the exact same body `B` and the same `hmac-sha256` header value to the app's webhook endpoint, but rewrites `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. The host app calls `ShopifyAPI::Webhooks::Registry.process(request)`. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and it matches, so validation succeeds: [7](#0-6) 
4. The registered handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, and the host app processes attacker-controlled data as belonging to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
