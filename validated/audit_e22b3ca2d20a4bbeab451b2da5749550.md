### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook by HMAC-validating only the raw request body, then hands the caller-supplied `shop-domain` header straight through to the app's handler as trusted tenant metadata. The `shop` value is never part of the signed material, so an attacker who can obtain one validly-signed webhook body/HMAC pair (e.g. by owning/installing the app on their own store) can replay that same body+HMAC to the webhook endpoint with an arbitrary `shop-domain` header and have it accepted as coming from a different, victim shop.

### Finding Description
`Utils::HmacValidator.validate` computes the signature exclusively over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body — the `shop-domain` header is excluded from the signed bytes: [2](#0-1) [3](#0-2) 

`Registry.process` checks the HMAC and then immediately forwards `request.shop` (parsed straight from the unauthenticated header) to the app-supplied handler as if it were a verified tenant identifier: [4](#0-3) 

The gem's own documentation instructs integrators to treat `data.shop` as "The shop domain of the webhook" — i.e., an authenticated field safe to use for tenant routing/lookups — with no caveat that it is unauthenticated: [5](#0-4) 

This is the same class of bug as the report's `int256`/`uint256` casting issue: a piece of data that is *acted upon* by downstream logic is not actually covered by the integrity check that is supposed to protect the whole message. Here the equality that should hold is:

`shop identity trusted by the handler == shop identity cryptographically bound by the HMAC`

but in reality:

`shop identity trusted by the handler == raw "shop-domain" header value (attacker-controlled, unsigned)`
`shop identity cryptographically bound by the HMAC == only the raw body bytes`

### Impact Explanation
Any unprivileged internet user who can install the target app on a store they control (a normal, free action for any Shopify merchant) will legitimately receive webhooks with a valid HMAC computed against their own body content using the real `api_secret_key`. Because the header `shop-domain` is not part of the signed payload, the attacker can POST the same `raw_body` + valid `x-shopify-hmac-sha256` value to the app's webhook endpoint while substituting an arbitrary `shop-domain` value naming a different, victim tenant. `Registry.process` will accept this as a validly-signed webhook and pass the forged shop identity to the app's handler. If the host app relies on `data.shop` to select which tenant's data/session to update (which is exactly what the gem's documentation recommends), this results in cross-tenant data injection/corruption — data intended for the attacker's own shop is attributed to and processed under a victim shop's identity.

### Likelihood Explanation
Likelihood is high for any app that follows the gem's documented pattern of trusting `data.shop`: the attacker only needs a free trial/development store to install the app on, capture one legitimately signed webhook body/HMAC pair for a topic the app subscribes to, and replay it directly to the app's public webhook endpoint with a modified header. No access to `api_secret_key`, access tokens, or any privileged Shopify account is required.

### Recommendation
Bind the shop identity to the signed content, not to an unauthenticated header:
- Include the `shop-domain` (and ideally `webhook-id`/`topic`) values in the HMAC-signed material, or
- Cross-check the header-supplied `shop` against an independent authenticated source before trusting it downstream (e.g., verify the shop is one for which the app currently holds a valid, previously-established webhook registration/session, and reject mismatches), and
- Update `docs/usage/webhooks.md` to explicitly document that `data.shop` is not covered by the HMAC and must not be treated as a trusted tenant identifier on its own.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a subscribed webhook topic (e.g. `orders/create`), capturing the raw body `B` and the resulting valid header `x-shopify-hmac-sha256: H` (computed by Shopify using the real `api_secret_key`).
2. Attacker sends a POST directly to the app's webhook endpoint with:
   - body: `B` (unchanged, so `HmacValidator.validate` succeeds against `H`)
   - header `x-shopify-shop-domain: victim.myshopify.com` (forged)
3. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header; `Registry.process` validates the HMAC (which only covers `B`) and succeeds, then invokes the handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...)`.
4. Any app logic keyed on `data.shop` (as recommended in `docs/usage/webhooks.md`) processes the attacker's data under the victim tenant's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
