This confirms the gem's own documentation (`docs/usage/webhooks.md#L125`) states that `Registry.process` "will verify the request did indeed come from Shopify" — but that verification only covers the raw body, not the `shop` field that the handler is told to trust as the tenant identifier.

### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic for a given shop once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC signature only ever covers the raw request body, never the `shop` header. `Request#shop` is read straight from an unauthenticated header and passed unchanged into `WebhookMetadata`, which host apps use as the tenant key.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` [2](#0-1) . The `shop` accessor, however, is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to that signature [3](#0-2) .

`Registry.process` only calls `Utils::HmacValidator.validate(request)`, and on success immediately forwards `request.shop` into `WebhookMetadata` for the app's handler to trust [4](#0-3) . The gem's own documentation instructs handler authors that `data.shop` is "the shop domain of the webhook" and that `process` "will verify the request did indeed come from Shopify" [5](#0-4) [6](#0-5) , i.e. the gem presents `shop` as an authenticated, trustworthy tenant identifier once `process` succeeds.

The identity binding broken is: **shop authenticated by HMAC ≠ shop stored/used as the tenant key**. Because the app's `api_secret_key` is shared across every merchant install of the app (it is not per-shop), any party who legitimately receives one genuine webhook delivery for their own shop possesses a `(raw_body, hmac)` pair that is valid under that shared secret regardless of which shop it was originally addressed to. Replaying that same body+HMAC pair while substituting a different `shop-domain` header value still passes `HmacValidator.validate`, because the header is never part of the signed material.

### Impact Explanation
This crosses the "shop authenticated versus shop stored as session key" boundary called out in the rules: a request that is cryptographically valid (came from Shopify's signing key for the app) can be attributed to an arbitrary victim shop chosen by whoever controls the replay, causing the host application to process attacker-controlled/foreign data under another tenant's identity — a cross-tenant data integrity/confusion issue. Depending on how the host app uses `data.shop` (e.g., to select which shop record to update, or to route the payload) this can lead to writing or acting on another merchant's data using a forged shop attribution.

### Likelihood Explanation
Exploitation requires the attacker to already be a webhook recipient for some shop under the same app (e.g., a malicious or compromised merchant installation) to obtain one genuine `(body, hmac)` pair, then replay it toward the app's webhook endpoint with a modified `shop-domain` header pointed at a victim shop. No access to `api_secret_key` or any access token is required — only capture/replay of a previously delivered, legitimately signed webhook body, which is plausible for any merchant that has installed the app.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) values in the HMAC-signed material, or otherwise cryptographically bind them to the verified body (e.g., verify that the `shop` header matches a shop the app currently has an active webhook registration for, and reject if the HMAC-verified body's own embedded shop/resource ownership disagrees with the header). At minimum, document that `WebhookMetadata#shop` is not independently authenticated by `Registry.process` and must be cross-checked against known installed shops before being used as a tenant key.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the same app,
# so they receive a genuine webhook delivery signed with the app's shared api_secret_key:
body = '{"id":1,"resource":"anything"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_api_secret_key, body)

# This (body, hmac) pair is valid and was delivered with:
# "shopify-shop-domain" => "attacker-shop.myshopify.com"

# Attacker replays the SAME body+hmac to the app's webhook endpoint,
# but swaps only the (unsigned) shop header to a victim shop:
forged_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => Base64.encode64(hmac),
  "shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unsigned
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) succeeds (only body is checked),
#    handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker's body)
```
`ShopifyAPI::Utils::HmacValidator.validate` only checks `request.hmac` against `request.to_signable_string` (the raw body) [7](#0-6) , so the forged `shop-domain` header passes unchecked into the handler [8](#0-7) .

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

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
