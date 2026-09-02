This confirms the finding: the documentation explicitly tells developers that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" via HMAC, and the handler is told to trust `data.shop` as "The shop domain of the webhook" [1](#0-0) , [2](#0-1) . But the `shop` value is read straight from the `x-shopify-shop-domain` header and never included in the HMAC computation.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `api_version`, and `webhook_id` directly from HTTP headers, but `Utils::HmacValidator` only ever authenticates the raw request body. Any attacker who can obtain one validly HMAC-signed webhook body (e.g. by installing the app on their own shop) can replay that same body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic and dispatch it to the handler under the attacker-chosen shop identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [3](#0-2) , and `HmacValidator.validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` [4](#0-3) . Meanwhile `Request#shop` (and `#topic`, `#api_version`, `#webhook_id`) are pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the signed body at all [5](#0-4) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before forwarding `request.shop` into `WebhookMetadata` and invoking the app's handler [6](#0-5) . Since the HMAC is computed with the app's `Context.api_secret_key`, which is shared across every shop that has installed the app, a body+HMAC pair that Shopify legitimately generated for one shop's webhook remains a valid signature for that same body regardless of what shop-domain header accompanies it. Note the contrast with `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` **is** explicitly included in `to_signable_string` and thus is properly bound to the HMAC [7](#0-6) . The webhook path lacks this equivalent binding.

This breaks the intended identity binding: `shop-domain header used to attribute/act on the webhook == shop actually authenticated by the HMAC`. In truth, the HMAC only authenticates "this body came from Shopify for *some* shop that installed this app," not "this body is associated with the shop named in this header."

### Impact Explanation
The gem's own documentation instructs developers to trust `Registry.process` as verifying "the request did indeed come from Shopify" and to use `data.shop` as the shop domain of the webhook [8](#0-7) [9](#0-8) . An app built per this guidance (as the reference `WebhookHandler` example shows, calling `perform_later(shop_domain: data.shop, webhook: data.body)` [10](#0-9) ) will process attacker-supplied body content under a victim's shop identity, since the handler has no independent way to detect the header/body mismatch. This is cross-tenant data confusion: attacker-controlled body content from their own shop's install gets attributed and persisted against a different, targeted `shop`, which can pollute or corrupt another merchant's data/state within the app.

### Likelihood Explanation
Exploitation only requires being an unprivileged internet user who can install the target app on a shop they control (a normal, unprivileged action for public apps) to receive a genuinely HMAC-signed webhook, and the ability to send a crafted HTTP request to the app's public webhook endpoint with a modified shop-domain header. No access to `api_secret_key`, tokens, or any privileged account is required.

### Recommendation
Bind the shop (and other trust-sensitive fields, e.g. topic) into the HMAC-verified signable content, or otherwise cryptographically/independently verify that the `shop-domain` header matches the shop that actually owns the webhook subscription (e.g. via `webhook_id` lookup against Shopify, or by only trusting `shop` values for shops with an active, previously-established session/webhook registration) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a real Shopify webhook (e.g. `orders/create`) with body `B` and a valid `x-shopify-hmac-sha256` computed over `B` using the app's shared `api_secret_key`.
2. Attacker captures this raw body `B` and its HMAC header value `H`.
3. Attacker sends `POST /callback/orders/create` to the target app with:
   - body: `B`
   - `x-shopify-hmac-sha256: H`
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `HMAC(secret, B)` [11](#0-10) .
5. The registered handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <parsed B>, ...)` [12](#0-11) , causing the app to process attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

### Citations

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
