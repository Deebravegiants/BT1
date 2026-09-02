This confirms the key finding. The library's documentation explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and that `data.shop` is "The shop domain of the webhook" [2](#0-1) , implying the `shop` field is authenticated. But the HMAC only ever covers the raw body, never the `shop` header.

### Title
Webhook `shop` field is trusted as authenticated tenant identity but is excluded from the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which computes the signature over `request.to_signable_string`. For `Webhooks::Request`, this signable string is defined as `@raw_body` only, never including the `shop-domain` header. Yet the same `process` call forwards `request.shop` — parsed directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header — into `WebhookMetadata`, which host application handlers use as the authenticated tenant identifier.

### Finding Description
The identity binding broken is:
`shop authenticated by HMAC` ≠ `shop consumed by the handler`

- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares to the `hmac` header. [3](#0-2) 
- `Webhooks::Request#to_signable_string` returns only `@raw_body`; it never mixes in `shop`, `topic`, or any header. [4](#0-3) 
- `Webhooks::Request#shop` is read straight from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with no cross-check against the HMAC or against any registered/authorized shop list. [5](#0-4) 
- `Registry.process` verifies only the HMAC, then immediately trusts `request.shop` to build `WebhookMetadata` passed to the app's handler. [6](#0-5) 
- The gem's own documentation tells integrators that `process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook," instructing handlers to treat it as trustworthy tenant context. [2](#0-1) [1](#0-0) 

Because a single app-level `api_secret_key` signs webhooks for every shop that installs the app (there is no per-shop signing key), the HMAC over the body is identical regardless of which shop it is "for." An attacker who controls a shop that has installed the same app (an unprivileged internet user, requiring only a free/dev Shopify store — no victim credentials, no `api_secret_key`, no access token) can:
1. Trigger a genuine webhook to their own endpoint (or capture the raw body + valid `x-shopify-hmac-sha256` for any webhook topic where the body content is attacker-influenceable, e.g. `products/update`, `orders/create` on their own store), giving them a `(raw_body, hmac)` pair valid under the shared secret.
2. Replay that exact `(raw_body, hmac)` pair directly to the app's own webhook endpoint, substituting the `x-shopify-shop-domain` header with the victim's shop domain.
3. `HmacValidator.validate` succeeds (it only checks `raw_body` against `hmac`), and `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`.

Before the request: `HMAC-verified data = raw_body`; `shop trusted by handler = victim-shop`. After: these remain unequal — the shop was never part of what the HMAC verified — yet the library presents them to the handler as a single validated unit.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce ("verify the request did indeed come from Shopify" for a given shop). Any handler that uses `data.shop` to key session lookups, trigger `client_credentials`/token-exchange refreshes, invalidate sessions on `app/uninstalled`, write per-shop state, or make authenticated Admin API calls (as the docs' own example does: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will act on forged tenant context supplied by an attacker who does not control that shop. This is a cross-tenant confusion vulnerability: an unprivileged app-installer can make the app process attacker-supplied payloads under another merchant's identity.

### Likelihood Explanation
High for any app that follows the gem's documented pattern of trusting `data.shop`. Exploitation requires no secrets beyond installing the app on any Shopify store (freely available), and no interaction with the victim; the attacker directly POSTs to the app's own public webhook endpoint. This is a single documented API call path (`Registry.process` → handler), not a misuse of an undocumented feature.

### Recommendation
Bind `shop` into the signable material used for the HMAC check, or explicitly validate `request.shop` against the set of shops actually authorized/installed for this app (e.g., cross-check against a session store) before constructing `WebhookMetadata`. At minimum, update `Webhooks::Request#to_signable_string` so the HMAC computation is scoped to a specific shop, or have `Registry.process` reject/flag when the header-derived `shop` cannot be independently corroborated.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the same app installed.
# Step 1: capture a real webhook body+hmac Shopify sent to the attacker's own endpoint
raw_body = '{"id": 1, "note": "malicious payload"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_api_secret_key, raw_body)
# (In practice the attacker captures this directly from a real Shopify-delivered webhook,
#  so they never need api_secret_key themselves.)

# Step 2: replay to the app's public webhook endpoint, spoofing the shop header
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-chosen, unverified
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) succeeds (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app now processes attacker-controlled data as if it came from victim-shop.
```

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
