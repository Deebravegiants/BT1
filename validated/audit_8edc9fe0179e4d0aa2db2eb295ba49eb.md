### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop` value that `ShopifyAPI::Webhooks::Registry.process` hands to the app's handler is read from an unauthenticated header. Any party who can obtain one validly-signed webhook (e.g. by installing the app on their own store) can replay it with a forged `shop` header to make the host app attribute that payload to a different tenant.

### Finding Description
`Request#to_signable_string` returns only the raw body, and `hmac` is derived purely from the `hmac-sha256` header: [1](#0-0) [2](#0-1) 

`shop` is pulled from a separate, unsigned header: [3](#0-2) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the body) against the HMAC — it never incorporates `shop`: [4](#0-3) 

`Registry.process` treats a passing HMAC check as proof the whole request — including `shop` — is authentic, then forwards `request.shop` straight into the handler's `WebhookMetadata`: [5](#0-4) 

The library's own documentation reinforces the false assumption that the whole request, including the shop, is verified: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook." [6](#0-5)  and the handler contract explicitly documents `shop` as a trusted field of `data`. [7](#0-6) 

This is the same class of bug as the referenced report: an identifier used downstream to select behaviour/ownership (`shop`, analogous to `revenueContract`) is never checked against the value that was actually authenticated (the HMAC covers only the body, analogous to only the token balance delta being checked without validating `revenueContract` was registered). The broken identity binding is:
`shop authenticated by HMAC` (∅, not covered) ≠ `shop passed to the handler as the tenant/session key` (`request.shop`, taken from an arbitrary header).

### Impact Explanation
Because a single `client_secret`/API-key pair is shared across every shop that installs the app, any merchant (an ordinary, unprivileged internet user, not requiring any of the app's own credentials) can:
1. Install the app on their own store to receive a legitimately Shopify-signed webhook (valid HMAC over that body).
2. Replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain.
3. `HmacValidator.validate` still passes because the header isn't part of the signed content, and `Registry.process` calls the app's handler with `data.shop` set to the forged victim domain.

Since apps commonly use `data.shop` as the tenant/session key to look up records, update state, or dispatch background jobs, this results in cross-tenant data injection/corruption — a host app can be tricked into processing attacker-supplied data (fully controllable via the attacker's own store's resource state) under a different merchant's identity.

### Likelihood Explanation
Any developer who installs the app once (a normal, unauthenticated onboarding action available to any internet user) obtains a validly-signed webhook body/HMAC pair for their own store and can immediately replay it with a different `shop` header — no secrets, tokens, or privileged access are required beyond the ordinary app install flow.

### Recommendation
Bind `shop` (and other routing-relevant headers) into the signed payload verification, or otherwise cryptographically tie the claimed shop to the signature — e.g., include the shop domain in `to_signable_string`, or require the caller to independently confirm the `shop` header matches a shop with an active, previously-established session/webhook registration for that topic before trusting `data.shop`. At minimum, the documentation should not claim the "request" as a whole (including `shop`) is verified when only the body is HMAC-checked.

### Proof of Concept
```ruby
# Attacker installs the app on their own store "attacker.myshopify.com" and
# receives a legitimate webhook for topic "products/update":
raw_body = '{"id":123,"title":"whatever the attacker sets on their own store"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Attacker replays the SAME body + HMAC to the app's webhook endpoint,
# but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "products/update",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) returns true (only raw_body is checked),
# and the handler receives data.shop == "victim-shop.myshopify.com"
# even though the payload actually originated from the attacker's own store.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
