### Title
Webhook `shop-domain` (and `topic`) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as fully authenticated once `Utils::HmacValidator.validate` succeeds, but the HMAC signature computed by the gem only covers the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — which the gem hands to the app's handler as the trusted identity of the tenant and event — are never part of the signed material. Any user who can obtain one genuinely-signed webhook body/HMAC pair from their own shop can resubmit it to the app's public webhook endpoint with a different `shop-domain` header and have it accepted as authentic, letting them inject data attributed to another merchant's tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature exclusively against `to_signable_string` (the body), never the headers: [3](#0-2) 

`Registry.process` uses this single HMAC check as the sole authentication gate, then forwards the *unverified* `request.shop` and `request.topic` straight to the app's handler as the trusted webhook metadata: [4](#0-3) 

This is exactly the documented, intended usage of the gem — the docs explicitly tell integrators to trust `data.shop` as "The shop domain of the webhook" and to key background work off it: [5](#0-4) 

Since `api_secret_key` is shared across *all* shops that install the app, any installed merchant can obtain a validly-signed `(raw_body, hmac)` pair for their own store (Shopify sends it to their own registered callback URL, which they control/observe), then POST that same body+HMAC to the app's public webhook endpoint with the `shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspected the header, and `Registry.process` dispatches to the handler with `shop: <victim-shop>`, breaking the equality that the app depends on: `shop authenticated by HMAC == shop attributed to the event`.

### Impact Explanation
This breaks the tenant isolation the gem is supposed to enforce for webhook delivery: an attacker who is a legitimate merchant of the app (i.e., an "unprivileged" party with respect to any other tenant) can make the app believe and process arbitrary webhook payloads as originating from a different shop. Depending on what the host app's handler does with `data.shop` (e.g., look up that shop's session/access token and perform mutations, enqueue jobs keyed by shop, update local per-shop records), this enables cross-tenant data corruption/impersonation — categorized as Critical (cross-tenant access) per the given impact taxonomy.

### Likelihood Explanation
Any merchant who installs the app can trivially capture one genuine webhook body/HMAC pair sent to their own endpoint (webhooks are plain HTTP POSTs, easily logged/proxied by the receiving app owner or by a party controlling that callback path) and replay it against the app's public webhook URL with a forged `shop-domain` header. No access token, `client_secret`, or privileged access is required — only the ability to send an HTTP request, which matches the "unprivileged internet user" threat model.

### Recommendation
Bind the identifying headers into the signed material verified by the gem, or otherwise ensure `shop`, `topic`, `webhook_id`, and `api_version` cannot be altered independently of the signature. Concretely:
- Have `VerifiableQuery#to_signable_string` for webhook requests include the `shop-domain` (and ideally `topic`, `webhook-id`) alongside the body before HMAC computation, or
- Have `Registry.process` independently corroborate `request.shop` against an out-of-band trusted value (e.g., cross-check against the webhook subscription/session the app registered) rather than trusting the header verbatim, and document that host apps must not rely solely on `data.shop` from an HMAC-passed request without this additional binding.

### Proof of Concept
1. Attacker installs the target app for `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify (or the attacker, triggering an event in their own store) sends a POST to the app's webhook endpoint with headers:
   - `x-shopify-hmac-sha256: <valid HMAC over raw_body computed with the app's shared api_secret_key>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
   - body: `{...attacker-controlled order JSON...}`
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value (it is delivered to an endpoint they control).
4. Attacker POSTs the identical `raw_body`/HMAC to the same app webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` succeeds (line 190 `.rb` in `registry.rb`) because only `raw_body` is checked; `Registry.process` calls the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)`, so the app processes attacker-controlled data as if it belonged to `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
