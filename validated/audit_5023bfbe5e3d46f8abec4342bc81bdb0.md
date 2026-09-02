Confirmed: the gem's own documentation explicitly instructs developers to trust `data.shop` (`docs/usage/webhooks.md` lines 12-27) as the shop-domain identity for a webhook, and `ShopifyAPI::Webhooks::Registry.process` documentation states verification "will verify the request did indeed come from Shopify" (line 125) — implying the whole payload, including the shop identity, is authenticated. In reality, only the raw body is HMAC-covered.

### Title
Webhook `shop` identity not covered by HMAC allows cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `WebhookMetadata` object whose `shop` field is taken directly, unauthenticated, from the `x-shopify-shop-domain` HTTP header. Because the header is not part of the signed content, an attacker who legitimately owns one shop can capture (or self-generate, since they control that shop) a valid `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint with the `shop-domain` header changed to a victim shop, and the request will pass verification while the handler treats it as belonging to the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, by contrast, is read straight from the `shop-domain` header with no cryptographic binding to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the signature only over `verifiable_query.to_signable_string`, i.e. the raw body — it never incorporates the `shop`, `topic`, `webhook_id`, or `api_version` headers: [3](#0-2) 

`Registry.process` treats a successful HMAC check as full authentication of the request ("Invalid webhook HMAC.") and then constructs `WebhookMetadata` using the unauthenticated `request.shop`, passing it straight to the app-supplied handler: [4](#0-3) 

The gem's own documentation instructs integrators to trust `data.shop` as "The shop domain of the webhook" and to key business logic (e.g. `shop_domain: data.shop`) off it, while describing `Registry.process` as verifying "the request did indeed come from Shopify": [5](#0-4) [6](#0-5) 

This breaks the intended identity binding: `shop header used by handler == shop covered by HMAC`. In reality `shop header used by handler != shop covered by HMAC` (the header is entirely outside the signed content), which is exactly the "field acted on but not covered by the HMAC" class of bug (analogous to the reported `mostRecentWithdrawalTimestamp` boundary issue, where a state-relevant value was excluded from the check that was supposed to bind it).

### Impact Explanation
Any internet user who can install the app on their own store (a normal, unprivileged action requiring no `api_secret_key`, access token, or leaked credential) can obtain a legitimately signed `(raw_body, hmac)` pair for a webhook topic of their choosing, with body content they fully control (e.g. `orders/create` for an order they create). They can then POST that same body/HMAC pair to the app's public webhook endpoint with the `x-shopify-shop-domain` header set to an arbitrary victim shop domain. `Registry.process` will accept it as valid and dispatch attacker-controlled data to the handler tagged as belonging to the victim shop, resulting in cross-tenant data injection/corruption in any host application that uses `data.shop` to key per-tenant storage or logic — exactly as the gem's documentation instructs. This is a cross-tenant access impact.

### Likelihood Explanation
High. Webhook endpoints are public HTTP routes by design; no authentication beyond the HMAC check is required to reach `Registry.process`. Obtaining a valid `(body, hmac)` pair requires nothing more than installing the target app on an attacker-owned shop, which is normal, unprivileged usage of any public app. The only "difficulty" is knowing/guessing a victim shop's domain, which is generally public (`*.myshopify.com` is often discoverable or guessable) and requires no secret.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the authenticated content, not just the raw body. At minimum, the HMAC verification for webhooks should include the `shop-domain` header in the signed string it validates against, or `Registry.process` should independently verify that `request.shop` corresponds to a shop with an active, matching session that actually registered for that topic before invoking the handler. Document clearly that `data.shop` must not be treated as authenticated purely by virtue of `Registry.process` succeeding unless such additional binding is performed.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` (normal unprivileged flow).
2. Attacker triggers a real webhook (e.g. creates an order with attacker-chosen fields), causing Shopify to POST to the app's webhook endpoint with a body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(api_secret_key, B)`, plus `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `B` and `H` (e.g. via their own logging middleware, a proxy they control, or by using the Shopify admin's "send test webhook" feature which they can trigger for their own shop).
4. Attacker sends a new POST request directly to the app's public webhook route with the same body `B` and header `x-shopify-hmac-sha256: H`, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC over `B` only, which still matches `H`, so `Registry.process` proceeds.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to act on attacker-controlled data as if it came from `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L10-27)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
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
