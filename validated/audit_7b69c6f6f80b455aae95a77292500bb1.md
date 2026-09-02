## Analog Found

### Title
Webhook `shop` (tenant identity) is not bound to the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify," but the HMAC it checks only covers the raw request body. The `shop` value that identifies which merchant/tenant the webhook belongs to is taken from an HTTP header that is never included in the signed payload, so the tenant binding `shop_header == shop_that_produced_the_hmac` is never actually checked.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic binding to that body [2](#0-1) .

`Utils::HmacValidator.validate` computes an HMAC over `verifiable_query.to_signable_string` (i.e. the body only) using the app's shared `Context.api_secret_key`, and compares it to the `hmac` header [3](#0-2) .

`Registry.process` calls this validator and then, without any additional check that the `shop` header actually belongs to the signer of this body, immediately forwards `request.shop` to the app's handler as tenant-identifying metadata: [4](#0-3) .

Because `Context.api_secret_key` is the app's single client secret — identical for every shop that has installed the app — any attacker who controls one legitimately-installed shop (e.g. a free/dev store) can capture a valid `(raw_body, hmac)` pair from a real webhook delivery. That pair remains a valid signature for *any* `shop-domain` header value, since the header plays no role in signature computation. The attacker can replay the captured body+HMAC to the app's webhook endpoint while setting `x-shopify-shop-domain` to a victim shop's domain. `HmacValidator.validate` will accept it, and `handler.handle` will receive `WebhookMetadata` whose `shop` field is the victim's domain paired with attacker-chosen body content [5](#0-4) .

This matches the report's bug class exactly: a field that is acted upon (the `shop` used for tenant identification) is not covered by the HMAC that's meant to prove authenticity, just as the analog rule describes.

The gem's own documentation reinforces that developers are expected to trust the result of `process` as proof of Shopify origin, without instructing them to separately verify the `shop` value: "call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler" [6](#0-5) , and the example handler passes `data.shop` straight through to per-shop business logic (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [7](#0-6) .

### Impact Explanation
This breaks the identity binding between "the shop whose secret produced this HMAC" and "the shop the app processes the webhook as." Since `api_secret_key` is shared across all of an app's installations, an unprivileged attacker with any legitimate (even trial) install can forge webhook deliveries attributed to a different, victim merchant, causing the host app to write attacker-controlled data into or trigger actions against the victim's tenant records — a cross-tenant access/data-integrity violation attributable to a documented gem API whose safety claim ("this will verify the request did indeed come from Shopify") does not hold for the `shop` field.

### Likelihood Explanation
Requires only: (1) the app's webhook endpoint URL (typically discoverable/registered publicly), and (2) at least one legitimately installed shop under attacker control (trivial to obtain for public apps via app stores/dev stores) to harvest a valid `(body, hmac)` pair. No access to the victim's or the app's secrets is required.

### Recommendation
Bind tenant identity into the signed payload verification path: e.g., require callers to pass the expected/looked-up shop alongside verification and reject if it doesn't match a shop known to have that webhook subscription, or otherwise cryptographically tie the `shop-domain` header into the HMAC computation before trusting `request.shop`/`data.shop` for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` (a shop they control) and lets a normal webhook (e.g., `orders/create`) fire, capturing the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` — both valid because they're signed with the app's shared `api_secret_key`.
2. Attacker sends `POST /webhook-endpoint` to the target app with headers:
   - `X-Shopify-Topic: orders/create`
   - `X-Shopify-Hmac-Sha256: H`
   - `X-Shopify-Shop-Domain: victim.myshopify.com`
   - Body: `B` (attacker-controlled content from step 1, or any body sharing that valid HMAC).
3. `HmacValidator.validate` recomputes HMAC over `B` with the app's secret and it matches `H`, so verification passes [8](#0-7) .
4. `Registry.process` invokes the handler with `WebhookMetadata` where `shop == "victim.myshopify.com"` and `body` is the attacker's payload [5](#0-4) , causing the host app to process attacker data under the victim tenant's identity.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
