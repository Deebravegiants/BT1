This confirms the finding. The `shop-domain` header (and `topic`, `webhook-id`, `api-version` headers) are never included in the HMAC signature computation — only the raw JSON body is signed.This confirms the root cause: `HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, and for `ShopifyAPI::Webhooks::Request` that string is exactly `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers [2](#0-1)  and are never mixed into the HMAC computation. `Registry.process` validates only the HMAC-over-body and then trusts `request.shop` and `request.topic` verbatim when building the `WebhookMetadata` handed to the app's handler [3](#0-2) .

Since Shopify signs webhooks using the single, shared `api_secret_key` for the whole app (not a per-shop secret) [4](#0-3) , a given `(raw_body, hmac)` pair is valid globally, independent of which shop it was originally sent for. That breaks the identity binding `shop-domain-header == HMAC-signed-shop`. This is exactly the "field acted on but not covered by the HMAC" analog called out in scope, so it merits a report.

### Title
Webhook `shop-domain` (and `topic`/`webhook_id`) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read unauthenticated from HTTP headers. `HmacValidator.validate`/`Registry.process` verify the HMAC exclusively against the body, then forward the header-derived `shop` and `topic` values to the app's registered webhook handler as if they were verified.

### Finding Description
`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to `verifiable_query.hmac` [5](#0-4) . For webhooks, `to_signable_string` is defined as simply `@raw_body` [1](#0-0) , and `hmac` is decoded from the `hmac-sha256` header [6](#0-5) . Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from other headers with no cryptographic binding to the signature at all [2](#0-1) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body vs. HMAC) before dispatching the (unauthenticated) `shop` and `topic` values into `WebhookMetadata`, which is passed to the app's handler as the trusted identity of the originating shop [3](#0-2) . The `WebhookMetadata` struct's `shop` field is documented and expected to be the authenticated tenant identifier [7](#0-6) .

Because `api_secret_key` is a single app-wide secret shared by every installed shop (the same key used to validate OAuth HMACs and webhooks for all merchants) [8](#0-7) , any `(raw_body, hmac)` pair that is valid for one shop is equally valid for every other shop using this app — the signature carries no shop-specific binding. The binding that is broken is:
`shop-domain header used by the handler == shop that produced the HMAC-signed bytes` — but the right-hand side doesn't exist; the HMAC signs the body only, regardless of which shop's header accompanies it.

### Impact Explanation
An attacker who controls or has previously observed one valid `(raw_body, hmac)` pair for the app (e.g., from their own installed test shop, or from any webhook delivery they can capture) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header. `Registry.process` will validate the HMAC (since it's still correct for that body) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop [9](#0-8) . Any host application that uses `data.shop` to look up per-tenant records, gate authorization, or key data writes (a documented, expected usage pattern [10](#0-9) ) can be tricked into associating attacker-chosen webhook content with a different merchant's tenant — a cross-tenant data-integrity/confidentiality violation.

### Likelihood Explanation
Exploitation requires only the ability to send an HTTP POST to the app's public webhook endpoint plus one previously valid `(body, hmac)` sample — no access token, `client_secret`, or privileged account is needed. An attacker can trivially obtain such a sample from their own store's install of the target app (a normal, low-privilege interaction), then replay it against any other shop's data path exposed by the handler. This is a realistic, low-effort attack path.

### Recommendation
Bind the shop identity (and ideally topic/webhook id) into the signed material, or otherwise cryptographically tie the header-derived `shop` to the specific `hmac`/body pairing — e.g., verify the signature using a per-shop secret/offline access token context, or require the handler-facing `shop` field to be cross-checked against a shop known to have this webhook registered and reject mismatches. At minimum, document that `data.shop` in `WebhookMetadata` is not itself HMAC-verified and must not be trusted as an authenticated tenant identifier without additional verification (e.g., confirming a corresponding session/access token exists for that shop).

### Proof of Concept
```ruby
# Attacker first captures one legitimate (body, hmac) pair, e.g. from their own
# shop's webhook delivery for topic "orders/create":
raw_body = '{"id":1,"note":"legit order from attacker-shop"}'
hmac_b64 = "<value captured from a real Shopify webhook delivered to attacker's own shop>"

# Attacker replays the identical body+hmac but swaps the shop-domain header
# to target a different, unrelated merchant:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled value
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation passes (it only checks raw_body vs signature),
#    and the app's handler receives WebhookMetadata.shop == "victim-shop.myshopify.com"
#    even though the HMAC never covered that value.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
