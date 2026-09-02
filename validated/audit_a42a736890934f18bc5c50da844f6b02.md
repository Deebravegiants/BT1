### Title
Webhook shop-domain identity is unauthenticated / not covered by HMAC, allowing an attacker to spoof the tenant on a validly-signed webhook request - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body [1](#0-0)  while `shop` is read from the unsigned `x-shopify-shop-domain`/`shopify-shop-domain` header [2](#0-1) . `Utils::HmacValidator.validate` verifies only that string against the app's shared `api_secret_key` [3](#0-2) . `Webhooks::Registry.process` then forwards `request.shop` straight into `WebhookMetadata` used by the handler, with no further binding check [4](#0-3) .

### Finding Description
The identity binding that should hold is:
`shop == the tenant whose secret/content produced this HMAC`

In reality the gem only proves:
`HMAC(raw_body, api_secret_key) == received_hmac`

Because `api_secret_key` (the app's `client_secret`) is the **same value for every shop that installs the app** — it is not per-shop — a valid HMAC only proves "this body was signed with this app's secret", not "this body/shop pair came from Shopify for shop X". The `shop` value that the host application uses to route/attribute the webhook (`request.shop`, passed into `WebhookMetadata#shop`) is taken from a header that is completely outside the signed content [2](#0-1) [1](#0-0) .

An unprivileged user who installs the target app on their own (attacker-controlled) store legitimately receives real webhooks with a valid HMAC computed from the shared `api_secret_key` over a body they fully control (they can trigger arbitrary order/product/customer events in their own store). They can then replay that exact `raw_body` + `hmac` pair to the app's public webhook endpoint while swapping the `shop-domain` header to name a victim shop. `Utils::HmacValidator.validate` only checks the body/hmac pair and returns `true` [5](#0-4) ; `Registry.process` proceeds to dispatch the (attacker-controlled) payload tagged with the victim's shop domain to the handler [4](#0-3) .

### Impact Explanation
This breaks the tenant boundary the gem is supposed to establish for webhook processing: an attacker-controlled payload can be attributed to an arbitrary victim shop merely by forging a header, since the header is outside the HMAC's coverage while the shared-secret HMAC only authenticates the app, not the tenant. Any host application that trusts `WebhookMetadata#shop` (which the gem explicitly hands over as the "shop" identity for the event) to select which merchant's session/data to update is exposed to cross-tenant data confusion/injection — satisfying the Critical "cross-tenant access" bar, since the root cause (identity field excluded from the signed payload) is in this gem's `Request`/`Registry` implementation, not something the host app can fix without re-implementing verification itself.

### Likelihood Explanation
Requires only: (1) being able to install the target app on a shop the attacker controls — an ordinary, unprivileged action available to any internet user with a Shopify dev/partner account, not a leaked credential or admin access to the target; and (2) sending a crafted HTTP POST with the captured body/HMAC and a modified `shop-domain` header to the app's public webhook endpoint. No access to `api_secret_key`, tokens, or victim infrastructure is needed. This is straightforward to execute once the attacker understands that `shop` is unsigned metadata.

### Recommendation
Bind the tenant identity into the verified material: include the shop domain (and/or webhook id) inside the HMAC-signed string (or otherwise cryptographically bind header-derived `shop` to the signed body), or require the host application (and ideally the gem itself, e.g. in `Registry.process`) to cross-check `request.shop` against a shop value embedded in the verified body/registered session before dispatching to handlers.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and captures a real webhook delivery, e.g. `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of raw body under shared api_secret_key>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - raw JSON body `B` (fully attacker-controlled content, e.g. crafted order fields).
2. Attacker resends the identical raw body `B` and identical `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only from `raw_body` [1](#0-0)  and succeeds because the body is unchanged.
4. `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker payload>, ...)` to the registered handler [6](#0-5) , causing the host app to process attacker-supplied data under the victim tenant's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
