Confirmed: the docs (`docs/usage/webhooks.md:125`) explicitly state that `Registry.process` "will verify the request did indeed come from Shopify," and the implementation trusts `request.shop` for tenant identification, yet the HMAC signature only covers the raw body — never the `shop-domain` header. This is a genuine, reachable binding break, not merely a host-application misuse issue, since the gem's own `Registry.process` API passes the unauthenticated `shop` value straight to the handler under the documented guarantee that the sender was verified.

### Title
Webhook Shop-Domain Header Is Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before dispatching to the app's handler, but the HMAC signature it validates covers only the raw request body — not the `shop-domain` header that identifies which merchant/tenant the webhook belongs to. Any party who can obtain one validly-signed webhook body (e.g., by installing the app on their own shop) can replay that exact body to the app's public webhook endpoint with an arbitrary `shop-domain` header, and the HMAC check will still pass.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read directly from an unauthenticated header (`shop-domain`/`x-shopify-shop-domain`) with no cryptographic binding to that body [2](#0-1) .

`Registry.process` validates only this body-only HMAC via `Utils::HmacValidator.validate(request)`, and then forwards the unauthenticated `request.shop` straight into `WebhookMetadata` passed to the app's handler [3](#0-2) . `HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the provided digest — again, only over the body [4](#0-3) .

The documented contract for `Registry.process` is that it "will verify the request did indeed come from Shopify" before invoking the handler [5](#0-4) , and the handler documentation tells developers to trust `data.shop` as "The shop domain of the webhook" [6](#0-5) . In reality, `shop` is never bound to the signed payload, so the equality the gem claims to guarantee — `authenticated_sender == shop_in_header` — does not hold. Only `authenticated_sender == owner_of(raw_body)` holds.

**Exploit path (unprivileged internet user):**
1. An attacker becomes a legitimate (self-service) installer of the target app on their own shop — an ordinary, unprivileged action requiring no special credentials or access token belonging to any other tenant.
2. Shopify delivers the attacker a real webhook (e.g., `app/uninstalled`, which has an empty body `{}`, or any topic whose payload the attacker can predict/control) with a valid `X-Shopify-Hmac-Sha256` computed over that body using the app's shared `client_secret`.
3. The attacker POSTs that exact captured body directly to the app's public webhook endpoint, substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain (a value the attacker can guess, since shop domains are `{name}.myshopify.com` and often discoverable).
4. `HmacValidator.validate` succeeds because it only checks the body, and `Registry.process` dispatches the handler with `shop: <victim-domain>`.
5. If the host app uses `data.shop` to select or mutate per-tenant state (e.g., mark the victim's app installation uninstalled, invalidate their session, queue a job keyed by shop, or write to a per-shop record) — exactly as the gem's own documentation and example handler recommend — the attacker achieves a cross-tenant action against a shop they never installed the app on and never held credentials for.

### Impact Explanation
This breaks a tenant-identity binding the gem documents and guarantees ("verify the request did indeed come from Shopify" + trusted `data.shop`), enabling cross-tenant interference/spoofing purely from an unprivileged, self-service app install — no leaked secrets, no access tokens, and no privileged account required. This maps to the report's "Critical - cross-tenant access" impact class, since an attacker can cause the host app to act on/for a shop it does not control.

### Likelihood Explanation
Likelihood is moderate-to-high for apps that follow the gem's own documented pattern (using `data.shop` from `WebhookMetadata` to key per-tenant actions without independently re-verifying the shop against an existing session/install record). Becoming an app installer is a normal, unprivileged action for any public app; capturing a predictable-body topic (`app/uninstalled`, or any topic sent with `fields` filtering down to an empty/known body) is trivial once installed.

### Recommendation
Include the `shop` domain (and ideally `topic`/`webhook_id`) inside the HMAC-covered signable string, or have `Registry.process` independently verify that the `shop` header corresponds to a shop with an active, previously-established session/installation before invoking the handler, rather than trusting an unauthenticated header value as the tenant identity.

### Proof of Concept
```ruby
# Attacker step 1: install the app legitimately on their own shop "attacker.myshopify.com"
# Attacker step 2: capture a real webhook delivery, e.g. app/uninstalled with body "{}"
#   Headers include a valid:
#   X-Shopify-Hmac-Sha256: <valid HMAC of "{}" using the app's real client_secret>
#   X-Shopify-Shop-Domain: attacker.myshopify.com

# Attacker step 3: replay to the app's public webhook endpoint with a swapped shop header
require "net/http"
require "uri"

uri = URI("https://victim-app.example.com/callback/app/uninstalled")
req = Net::HTTP::Post.new(uri)
req["X-Shopify-Topic"] = "app/uninstalled"
req["X-Shopify-Hmac-Sha256"] = "<captured-valid-hmac-of-empty-body>"
req["X-Shopify-Shop-Domain"] = "victim-shop.myshopify.com" # forged, unauthenticated
req.body = "{}"

Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |http| http.request(req) }

# Server-side (per this gem's own code path):
# ShopifyAPI::Webhooks::Registry.process(
#   ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)
# )
# -> Utils::HmacValidator.validate(request) returns true (HMAC only checks body "{}")
# -> handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app now processes an "app/uninstalled" event attributed to a shop the attacker never installed on.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
