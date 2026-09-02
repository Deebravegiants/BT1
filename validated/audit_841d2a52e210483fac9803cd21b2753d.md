### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by verifying an HMAC over the raw request body only, but then trusts the `shop` value taken from an HTTP header that is *not* part of that signed content. Because the app's HMAC secret (`Context.api_secret_key`) is shared across every merchant that has installed the app, any tenant that has legitimately received a signed webhook can replay that exact body+signature to the app's webhook endpoint while substituting a different shop's domain in the header, and the signature will still validate — attributing attacker-controlled data to a victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` derives its signable content solely from the raw HTTP body: [1](#0-0) 

while `shop` is read straight from an unauthenticated header, entirely outside the signed material: [2](#0-1) 

`Registry.process` validates only that signature (i.e., only the body) and then forwards the header-derived, unauthenticated `shop` value straight to the handler as the trusted tenant identity: [3](#0-2) 

`Utils::HmacValidator.validate` simply recomputes the HMAC over `verifiable_query.to_signable_string` (the raw body, for webhooks) and compares it to the received signature — it never incorporates the `shop` header: [4](#0-3) 

Crucially, the secret used to sign/verify is the app's `client_secret`, shared by every shop that installs the app — not a per-tenant secret. This is the same secret used for OAuth token exchange: [5](#0-4) 

The identity binding that should hold is:
`shop asserted in the signed payload == shop attributed to the webhook by the gem`

Instead, the gem breaks this into two independent facts:
1. "this body was produced/forwarded by Shopify for *some* installer of this app" (proven by HMAC over body only), and
2. "this body belongs to shop X" (an unauthenticated header, never covered by the signature).

The gem's own documentation instructs host apps to treat `data.shop` as an authoritative field of the verified webhook: [6](#0-5) [7](#0-6) 

so a host app following the gem's documented API has no indication that `shop` requires independent verification — `Registry.process` presents it as already authenticated once `process` returns without raising.

### Impact Explanation
Any merchant/tenant that has installed the app (a normal, unprivileged install — no special access needed) can capture one of the legitimate webhook deliveries Shopify sends to their own store (body + `X-Shopify-Hmac-Sha256` value), then replay that exact HTTP request to the app's webhook endpoint while changing only the `X-Shopify-Shop-Domain` header to name a victim shop. Because the signature check ignores the header, `Utils::HmacValidator.validate` returns `true`, and `Registry.process` invokes the app's handler with `WebhookMetadata` claiming the (attacker-supplied) body belongs to the victim shop. This is a cross-tenant identity-binding bypass: an attacker-controlled tenant can inject data/events that the host app will process as if they originated from a different, victim tenant (e.g., poisoning per-shop caches/state, forging `shop/redact`/`customers/redact` compliance events, or corrupting business logic keyed by `shop`).

### Likelihood Explanation
High feasibility: the only prerequisite is that the attacker operates any shop that has installed the target app (installation is self-service and requires no special privilege), and can capture at least one webhook delivery to their own endpoint (trivial, since it is delivered to infrastructure they control). No access to the app's `client_secret`, access tokens, or the victim's credentials is required — only a replayed, previously-valid signed body with a swapped header.

### Recommendation
Bind the tenant identity into the material that is actually verified before it is trusted:
- Include the `shop` (and ideally `topic`, `webhook_id`) header values in the string that is HMAC-verified, or otherwise cryptographically bind them to the body, rather than trusting them as free-standing headers in `Webhooks::Request#shop`/`#topic`.
- Alternatively/additionally, require and check that the `shop` in each processed webhook matches a shop for which the app has an active, previously-established session/installation record before dispatching to handlers, so a replayed body cannot be re-attributed to an arbitrary tenant.
- Document clearly that `data.shop` in `WebhookMetadata` is not itself covered by Shopify's HMAC signature so host apps are not misled into treating it as verified.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets it deliver a legitimate webhook (e.g. `orders/create`) to the app's webhook endpoint; the attacker (controlling the endpoint) records the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` Shopify computed with the app's shared secret.
2. Attacker crafts a new HTTP POST to the same webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - Header `X-Shopify-Topic`: unchanged or attacker-chosen
3. The app calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: spoofed_headers))`.
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so validation passes (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: parsed(B) ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the host app to process attacker-controlled data as if it belongs to `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/auth/oauth.rb (L74-79)
```ruby
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }
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
