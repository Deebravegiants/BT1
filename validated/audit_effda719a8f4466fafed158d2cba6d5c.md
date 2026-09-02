This confirms the root cause. The gem's docs explicitly tell app developers `data.shop` is "The shop domain of the webhook" — a value they're expected to trust for tenant identification (`docs/usage/webhooks.md:14,125-126`) — but that value is populated straight from an HTTP header that the HMAC never covers.I have sufficient evidence to write up the finding.

### Title
Webhook `shop` domain is trusted for tenant identification but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body [1](#0-0) . The `shop` value that the gem hands to the app's webhook handler as the trusted tenant identifier is read directly from the `shop-domain` HTTP header, which is never included in the HMAC-signed bytes [2](#0-1) . This breaks the intended identity binding `HMAC-verified bytes == tenant-attributing fields`.

### Finding Description
`Registry.process` does two things: it verifies the HMAC via `Utils::HmacValidator.validate(request)`, and then constructs a `WebhookMetadata` object using `request.shop`, which is handed to the app-provided handler as the authoritative tenant for that event [3](#0-2) .

The HMAC verification only covers `@raw_body`: [4](#0-3) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from attacker-controllable HTTP headers, none of which participate in `to_signable_string`: [5](#0-4) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it only against the `hmac` header — it never binds `shop` into the signature: [6](#0-5) 

Because the app's `api_secret_key` is shared across every shop the app serves, any unprivileged user who can install the app on their own store (an ordinary Shopify merchant, requiring no privileged access to the app or to another merchant's store) can:
1. Trigger a real webhook to their own shop's endpoint and capture the raw body and its valid `x-shopify-hmac-sha256` value (this HMAC is valid for that exact body regardless of which shop it's attributed to, since `shop` isn't part of the signed content).
2. Replay that identical `raw_body` + `hmac` header pair to the app's webhook endpoint, but substitute an arbitrary `x-shopify-shop-domain` header value naming a different, victim shop.
3. `HmacValidator.validate` succeeds (the body/HMAC pair is genuinely valid), and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

The gem's own documentation instructs app authors to treat `data.shop` as the authoritative shop identity for routing/tenant lookups (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), reinforcing that this is the gem's documented contract, not host misuse [7](#0-6) , and states that `process` "will verify the request did indeed come from Shopify" [8](#0-7) , implying the whole payload — including `shop` — is authenticated, which it is not.

### Impact Explanation
This allows cross-tenant data confusion/spoofing: an attacker who legitimately controls one tenant (their own installed shop) can make the app process attacker-supplied webhook content under a different, victim tenant's identity. Depending on how the host app uses `data.shop` (commonly to look up that shop's session/access token or to write into that shop's records, as the docs themselves suggest), this can lead to cross-tenant data injection or corruption of a different merchant's data using only a webhook the attacker fully controls the body of. This matches the Critical category of "cross-tenant access."

### Likelihood Explanation
Likelihood is high for any app that follows the gem's documented webhook pattern: the attacker only needs their own (free/trial) shop installation of the target app — no leaked secrets, no privileged access to the victim, and no TLS interception. Constructing the forged header/body/HMAC replay requires only observing one legitimate webhook delivery to the attacker's own store.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signed content, or independently verify that the `shop-domain` header matches a shop the app has a valid, previously-established session/subscription for before trusting it, rather than exposing the raw unauthenticated header value as `WebhookMetadata#shop`.

### Proof of Concept
```ruby
# Step 1: attacker installs the app on their own shop "attacker.myshopify.com"
# and triggers any webhook (e.g. orders/create), capturing:
raw_body = '{"id":1,"note":"hi"}'
valid_hmac = "<value of x-shopify-hmac-sha256 header from the real delivery>"

# Step 2: attacker replays the exact same body + hmac to the app's webhook
# endpoint, but swaps the shop-domain header to a victim shop they do not control:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,       # still valid: HMAC only signs raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (body/HMAC pair is genuinely valid)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app's handler now processes attacker-controlled body data as belonging to victim-shop.
```

### Citations

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
