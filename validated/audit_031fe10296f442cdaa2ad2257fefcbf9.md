### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body, computed with the app's single, shop-agnostic `api_secret_key`. The `shop` value that the framework hands to the app's handler (`WebhookMetadata#shop`) is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is never included in the signed content. Any party who can obtain one valid signed webhook body (e.g., a merchant using the app who receives legitimate webhooks for their own store) can replay that same body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the request will pass verification as if it originated from a different shop.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the HMAC over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body: [2](#0-1) 

Meanwhile the `shop` accessor, which becomes the tenant identifier passed to the app's handler, is pulled straight from an HTTP header with no cryptographic binding to the signature: [3](#0-2) 

`Registry.process` only checks the HMAC before dispatching to the handler with the attacker-controlled `shop`: [4](#0-3) 

This breaks the identity binding: `shop that authenticated the HMAC == shop associated with signed bytes` is expected, but in reality `shop delivered in an unauthenticated header ≠ shop bound by the HMAC`. Because `api_secret_key` is the app's single client secret shared across every installed shop (not a per-shop secret), a valid HMAC only proves the body was produced using that shared secret — it proves nothing about which shop the payload is "for." The documented consumption pattern explicitly trusts `data.shop` as the tenant key once `Registry.process` succeeds: [5](#0-4) 

### Impact Explanation
An unprivileged attacker who is a legitimate merchant of the app (or anyone who can capture one valid, HMAC-signed webhook body sent to their own shop) can replay that exact body with a forged `shopify-shop-domain` header naming a victim shop. Since the header is outside the signed content, the forged request still passes `HmacValidator.validate`. If the host application (as the gem's own documentation recommends) uses `data.shop` to select which shop's session/access token/tenant data to act on, the attacker can inject attacker-controlled webhook content attributed to a shop they do not control — a cross-tenant data confusion driven entirely by a header that carries no authentication.

### Likelihood Explanation
Medium-High: the attacker needs only to be a legitimate, already-onboarded merchant of the target app (no special privilege, no access token, no `client_secret` needed) and to capture one of their own legitimately delivered webhooks (trivial, since they control the endpoint or can observe request logs). No cryptographic secret needs to be broken; only the unauthenticated header needs to be changed.

### Recommendation
Bind the `shop` claim to the signed content instead of trusting an unauthenticated header. Concretely, `Request#shop` (and any downstream use in `WebhookMetadata`) should be excluded from trust unless corroborated by data actually covered by the signature (e.g. cross-checking against a shop value embedded in the JSON body, or by having the host maintain per-shop webhook secrets/registration bookkeeping instead of relying on the header). At minimum, the library's documentation should not present `data.shop` as if it were verified, since nothing in `to_signable_string` covers it.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook, receiving legitimate deliveries from Shopify with a valid `x-shopify-hmac-sha256` computed over the raw JSON body using the app's shared `api_secret_key`.
2. Attacker captures one such request: `raw_body` + `x-shopify-hmac-sha256` header.
3. Attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only hashes `raw_body`, which is unchanged.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches to the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and the app processes attacker-supplied content as if it belonged to the victim shop.

### Citations

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

**File:** docs/usage/webhooks.md (L10-30)
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
  end
end
```
```
