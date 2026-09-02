I have enough information to complete the analysis.

### Title
Webhook `shop-domain`, `topic`, and `webhook_id` headers are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates an inbound webhook only by checking the HMAC over the raw request body, then unconditionally trusts the `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers when building the `WebhookMetadata` passed to the app's handler. Because the signature covers only the body, an attacker who can obtain one genuine `(body, hmac)` pair signed with the app's shared `client_secret` can replay it with a forged `shop-domain`/`topic` header set, and the check will still pass.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the signature purely against `verifiable_query.to_signable_string`, i.e. the raw body, using the app's `Context.api_secret_key`: [2](#0-1) 

`Registry.process` uses this body-only HMAC check as its sole authenticity gate, then builds `WebhookMetadata` directly from the *unauthenticated* headers (`request.shop`, `request.topic`, `request.webhook_id`, `request.api_version`) and hands them to the app's registered handler: [3](#0-2) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors simply read HTTP headers with no cryptographic binding to the body or to each other: [4](#0-3) 

The identity binding that should hold is: `hmac_signed(shop-domain header) == shop-domain header used to attribute the webhook to a tenant`. In this implementation that equality does not hold — the HMAC only proves "this body byte-string was produced (or replayed) using the app's secret"; it proves nothing about which shop, topic, or webhook id the body belongs to. This is the same bug class as the linked report: a value is acted upon (chain tip / blockheight-blockhash pairing in the Bitcoin case; here, the shop/topic/webhook_id triplet) without being consistently bound to the value that was actually verified (cs_main-protected chain state there; the signed raw body here).

Because the `client_secret` is shared across every shop that installs the app, any entity capable of triggering a legitimate webhook delivery for *any* single shop (e.g., a merchant installing the app on their own store — an "unprivileged" actor with respect to other tenants) can capture a valid `(body, hmac)` pair. That pair can then be replayed directly against the app's public webhook endpoint with attacker-chosen `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers, and `Registry.process` will accept it as an authentic webhook for the *victim* shop.

The gem's own documentation reinforces the (incorrect) expectation that `process` fully authenticates the request: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook," with no caveat that the shop/topic/id headers are unauthenticated: [5](#0-4) 

### Impact Explanation
This breaks the tenant (shop) identity binding at the point where an app decides which merchant's data/state to update from a webhook. A downstream handler (as shown in the gem's own doc example, which forwards `data.shop`/`data.body` into a job queue keyed by shop) can be made to apply attacker-influenced webhook data under another merchant's `shop` identity — i.e., cross-tenant data injection/misattribution, which is explicitly listed as Critical impact in the rules ("cross-tenant access").

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the app on any one shop (or otherwise cause one legitimate webhook delivery, e.g. via a trial/dev store — not a privileged account relative to the victim tenant), and (2) capturing that single valid `(raw_body, hmac)` pair (visible at the attacker's own endpoint) and replaying it with forged headers to the app's public webhook URL. No access to `api_secret_key`, access tokens, or the victim's credentials is required, matching the "unprivileged internet user" threat model.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook_id` headers in the signable content that the HMAC is computed and verified over (or otherwise cryptographically bind them to the body), so `Utils::HmacValidator.validate` fails if any of these attributes are altered relative to what Shopify actually signed. At minimum, document prominently in `docs/usage/webhooks.md` that `Registry.process`'s HMAC check authenticates only the body and that host applications must independently verify the `shop-domain` header against a shop they have on record before trusting it as a tenant identifier.

### Proof of Concept
```ruby
# 1. Attacker installs TargetApp on their own shop "attacker.myshopify.com"
#    and receives a genuine webhook delivery, e.g.:
raw_body = '{"id":1,"note":"hi"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_CLIENT_SECRET, raw_body)
b64_hmac = Base64.encode64(hmac)   # this is a VALID signature for raw_body, computed by Shopify

# 2. Attacker replays the same body+hmac directly at the app's public webhook
#    endpoint, but swaps the shop-domain/topic headers to point at a victim shop:
headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => b64_hmac,                 # unchanged, still matches raw_body
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id"   => "forged-id",
  "x-shopify-api-version"  => "2024-01",
}

# 3. Registry.process accepts it, because HmacValidator.validate only checks raw_body:
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: {...}, ...))
# The app's handler now processes attacker-controlled body content under victim-shop's identity.
``` [6](#0-5)

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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
