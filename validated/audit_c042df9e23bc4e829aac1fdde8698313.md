### Title
Webhook `shop-domain` (and `topic`/`api-version`/`webhook-id`) header is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop-domain` HTTP header (along with `topic`, `api-version`, `webhook-id`) to build the `WebhookMetadata` that is handed to the host application's handler. Because the HMAC never binds the `shop-domain` header to the signed bytes, an attacker who can obtain any one valid `(body, hmac)` pair signed with the app's shared `client_secret` — trivially available to them by installing the app on their own shop and receiving a legitimate webhook — can replay that exact body/HMAC pair while substituting an arbitrary victim `shop-domain` header. The gem will accept it as authentic and dispatch it to the host app labeled as coming from the victim shop.

### Finding Description
The equality the code is supposed to enforce is:
`shop attributed to the processed event == shop that Shopify's HMAC signature actually authenticates`

In `Registry.process`:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [1](#0-0) 

`Utils::HmacValidator.validate` only ever signs/verifies `verifiable_query.to_signable_string`:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw body, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated headers and are never included in the signed bytes:
```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
``` [3](#0-2) 

So the "bytes verified" (raw body only) and the "bytes/field acted upon" (`shop-domain` header used to attribute the event to a specific merchant) are two different things — exactly the identity-binding gap described in the reference bug class, just manifested as a header-vs-signed-payload mismatch instead of an accounting mismatch. Since a single app has one shared `api_secret_key` across all shops that install it, any attacker who is (or controls) a legitimate installed shop can generate a perfectly valid `(body, hmac)` pair for content they choose (e.g., by triggering a real webhook, such as `orders/create`, with attacker-controlled order data on their own store), then resend that exact body and HMAC to the app's webhook endpoint with a forged `shop-domain`/`x-shopify-shop-domain` header naming a different, victim shop. `HmacValidator.validate` will succeed (the body's signature is genuinely valid for that shared secret), and `Registry.process` will pass `shop: <victim-shop>` to the host application's webhook handler.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook consumers: it allows an unprivileged attacker (any shop that has installed the app) to inject fabricated, attacker-chosen event data into the host application's per-tenant processing pipeline under a different (victim) shop's identity, with no credentials belonging to that victim shop. Depending on how the host app uses `WebhookMetadata#shop` (typical patterns: looking up the victim's stored session/access token to act on their behalf, updating victim-shop business records, billing, or app state), this constitutes cross-tenant access/confusion — data intended to be scoped to one merchant can be forged into another merchant's context purely by controlling the header, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is significant: the only prerequisite is having (or creating) any single shop installation of the target app to legitimately receive at least one valid webhook `(body, hmac)` pair — no access to `api_secret_key`, access tokens, or the victim's credentials is required. The attacker fully controls the HTTP headers of the replayed request (this is a direct HTTP call to the app's own webhook endpoint, not mediated by Shopify), and the gem performs no binding check between the signed body and the `shop-domain` header before invoking the handler.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`api-version`/`webhook-id`) header into the HMAC verification so the signature cannot be reused across shops or resource identifiers. Concretely, `Request#to_signable_string` should incorporate the shop-domain header (and other trust-relevant headers) rather than the raw body alone, or `Registry.process` should independently cross-check the header-derived shop against known deliveries. At minimum, `Registry.process` should require the host app to treat `request.shop` as untrusted metadata unless it is separately corroborated (e.g., via the `webhook_id` looked up against Shopify's Admin API for the shop the app believes it is processing for).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a real webhook (e.g., `orders/create`) with attacker-controlled order JSON as the raw body `B`. Shopify sends the request with a valid `x-shopify-hmac-sha256` header `H = HMAC-SHA256(client_secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures `B` and `H` from their own delivery (or from their own server logs).
3. Attacker sends a new POST directly to the app's webhook endpoint with the exact same raw body `B` and `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(client_secret, B)` and matches `H` — validation passes, since the body/HMAC pair truly is valid for this app's shared secret.
5. `request.shop` returns `"victim.myshopify.com"` from the (unauthenticated) header, and `Registry.process` invokes the host app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the attacker-supplied event/body to be processed as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
