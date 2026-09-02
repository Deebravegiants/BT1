This confirms the finding. The gem's documented API explicitly instructs host apps to trust `data.shop` from `WebhookMetadata` (see `docs/usage/webhooks.md:12-17,125`), and `ShopifyAPI::Webhooks::Registry.process` treats `Utils::HmacValidator.validate(request)` as sufficient authentication before dispatching `data.shop` to the handler [1](#0-0) . However, the HMAC only signs the raw body, never the shop-domain header.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes/exposes the `hmac` used for verification from the `hmac-sha256` header and defines `to_signable_string` to return only `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from separate, unauthenticated headers [3](#0-2) . `Utils::HmacValidator.validate` only verifies `verifiable_query.to_signable_string` against `verifiable_query.hmac` [4](#0-3) , so the shop-domain header is never bound to the signature. `Registry.process` treats a passing HMAC check as proof the request is authentic for the shop indicated by `request.shop`, and forwards that unauthenticated shop value straight to the app's handler [5](#0-4) . The gem's own documentation instructs apps to key their business logic off `data.shop` from this same flow [6](#0-5) .

### Finding Description
The security-relevant binding this vulnerability breaks is:

`shop asserted in the "x-shopify-shop-domain" header == shop the app's data is actually associated with`

That equality should be guaranteed by the HMAC, since it is the app's only cryptographic authentication mechanism for inbound webhook requests. But the signed content is only the JSON body (`@raw_body`), and the app's `client_secret`-derived signing key is identical for every shop that has installed the app — it is not per-shop. Consequently, a merchant who has legitimately installed the app on their own store (shop A) receives genuinely signed webhook deliveries. Because the signature never binds to shop A's domain, that attacker can:
1. Capture a real webhook body + valid `x-shopify-hmac-sha256` value delivered to their own installation.
2. Replay the exact same body/HMAC to the app's public webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop B's domain.
3. `HmacValidator.validate` still succeeds (it never inspected the header), `Registry.process` extracts `shop: request.shop` = shop B, and the app's handler processes/persists this forged event as if it originated from shop B [7](#0-6) .

This is a direct violation of the tenant isolation the HMAC is supposed to enforce, and it is fully reachable through the gem's own documented, unmodified API — no host-application misuse is required.

### Impact Explanation
This meets the Critical bar of "cross-tenant access": an attacker who is merely a customer/merchant of the app (an "unprivileged internet user" relative to other tenants) can inject data attributed to an arbitrary victim shop into any topic the app has registered (e.g. `orders/create`, `app/uninstalled`, `customers/data_request`), corrupting per-tenant state, triggering unauthorized actions keyed by shop domain, or forging mandatory GDPR webhooks for a shop the attacker doesn't control.

### Likelihood Explanation
Likelihood is high: the attacker only needs their own legitimate app installation (a low bar — installing a public app on a free dev store) to capture a valid body/HMAC pair, since the body content for many topics is attacker-influenced (e.g., updating their own shop's product/customer data triggers a webhook with attacker-chosen JSON) or at minimum replayable byte-for-byte. No access to the `client_secret`, access tokens, or any other shop's credentials is required — only header manipulation on a self-controlled HTTP client.

### Recommendation
Include the shop domain (and ideally topic/api-version) inside the HMAC-signed material, or otherwise cryptographically bind the shop header to the signature so `HmacValidator.validate` fails if that header is altered relative to what Shopify actually signed. At minimum, document that `request.shop`/`data.shop` must never be trusted for tenant-scoping decisions unless it is independently corroborated (e.g., cross-checked against the shop stored for the webhook's `webhook_id` in the app's own webhook registration state).

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and receives a legitimate webhook for it.
raw_body = '{"id":123,"note":"hi"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_CLIENT_SECRET, raw_body)

# Attacker replays the same body/hmac but swaps the shop-domain header to the victim's shop.
forged_headers = {
  "x-shopify-topic"       => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac), # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))
# The app now believes this attacker-crafted order event came from "victim-shop.myshopify.com".
```

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
