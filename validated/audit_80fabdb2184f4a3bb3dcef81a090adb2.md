Based on the analysis, the strongest reachable analog is the identity-binding gap in webhook processing: the HMAC only covers the request body, while `shop`, `topic`, and `webhook_id`—the values actually acted upon and handed to the app's handler—come from unauthenticated headers.

### Title
Webhook shop/topic identity not bound by HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers [2](#0-1) . `Webhooks::Registry.process` verifies the HMAC over the body only, then trusts `request.shop`/`request.topic` (header values) to dispatch the handler and build `WebhookMetadata` [3](#0-2) .

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` field [4](#0-3) . For webhooks, `to_signable_string` is exactly the raw body bytes — headers are entirely excluded from the signed material.

Because a single app's `api_secret_key` is shared across every shop/tenant that installs it, the HMAC only proves "this body+secret pair is valid for this app," not "this body came from this specific shop." An attacker who is themselves a legitimate (unprivileged) merchant/tenant of the app can:
1. Trigger or otherwise obtain one genuine webhook delivery for their own shop (body + valid `x-shopify-hmac-sha256`).
2. POST directly to the app's public webhook endpoint with the exact same body and HMAC header, but an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header pointing at a victim shop.
3. Because `to_signable_string` never includes these headers, `HmacValidator.validate` still returns `true`, and `Registry.process` calls the handler with `WebhookMetadata.new(shop: request.shop, ...)` [5](#0-4)  using the attacker-chosen (unauthenticated) shop value.

The binding broken is: `shop_that_the_HMAC_proves_authenticity_for == shop_identifier_the_application_acts_on`. That equality does not hold here — the gem hands the host application a `shop` value that was never covered by the cryptographic signature, yet apps are documented to key business logic (data association, billing, `app/uninstalled` cleanup, job routing) directly off `data.shop` [6](#0-5) .

### Impact Explanation
This crosses a tenant boundary: an attacker with no more privilege than "an installed merchant of the app" can make the application attribute webhook events (and any downstream side effects keyed on `shop`) to a different, victim shop of their choosing, without needing the app's `client_secret`/`api_secret_key`. Depending on how the host app uses `data.shop` (e.g., driving per-shop background jobs, cache/session keys, or uninstall/cleanup logic), this enables cross-tenant data corruption or spoofed lifecycle events — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likely (Moderate-High): the attacker only needs (a) their own legitimate app installation to obtain one valid body+HMAC pair, and (b) the ability to send an arbitrary HTTP POST to the app's public webhook URL with custom headers — both trivially available to any unprivileged internet user/merchant. No secret material needs to be known or guessed.

### Recommendation
Bind the shop/topic identity into the signed material, or otherwise independently verify it: e.g., include `shop-domain`/`topic`/`webhook-id` header values in `to_signable_string` (matching Shopify's actual signing scope if it changes), or require the host app to cross-check `request.shop` against the shop associated with the specific `webhook_id`/subscription that was registered via `Registry.register`, rather than trusting the header verbatim after only a body-HMAC check.

### Proof of Concept
```ruby
# Attacker is a legitimate merchant "attacker-shop.myshopify.com" with the app installed.
# They previously received (or triggered) a real webhook delivery for their own shop:
raw_body = '{"id":123,"note":"hello"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
) # attacker legitimately has this pair from their own shop's delivery

# Attacker POSTs directly to the app's public webhook endpoint, same body/hmac,
# but claims to be a victim shop:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unsigned
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body HMAC matches),
#    handler is invoked with shop: "victim-shop.myshopify.com"
```

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
