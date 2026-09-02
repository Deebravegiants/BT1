### Title
Webhook `shop` and `webhook_id` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verified by `Registry.process` authenticates the body bytes and the app's shared secret, but never binds the `x-shopify-shop-domain` or `x-shopify-webhook-id` headers to that signature. An attacker who can obtain any one validly-signed webhook body/HMAC pair (e.g., from their own development shop with the app installed) can replay that exact body to the app's public webhook endpoint while freely substituting the shop-domain and webhook-id headers, and the gem will still report the request as authentic.

### Finding Description
The claimed binding is: `HMAC-verified(raw_body) == (shop acted on, webhook_id acted on)`. Tracing the code shows this binding does not hold:

- `Request#to_signable_string` returns `@raw_body` only: [1](#0-0)  
- `shop` and `webhook_id` are read directly, unsigned, from headers: [2](#0-1) 
- `Registry.process` validates only the HMAC of the request via `Utils::HmacValidator.validate(request)`, then builds `WebhookMetadata` directly from the unauthenticated `request.shop` and `request.webhook_id` header values and dispatches to the handler: [3](#0-2) 
- `HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the raw body) and the app's `api_secret_key`/`old_api_secret_key`, with no reference to any header other than the received HMAC: [4](#0-3) 

No `ShopValidator.sanitize!` or any other shop-domain check is invoked anywhere in this webhook path (confirmed by tracing `Registry.process` and `Request`), so nothing constrains `request.shop` to belong to the tenant that actually produced the body.

Exploit flow: The attacker registers their own development shop and installs the target app (an action explicitly permitted for an unprivileged attacker). They receive a genuine webhook delivery from Shopify for their own shop, capturing `raw_body` and the valid `x-shopify-hmac-sha256` value (both computed with the app's real, but attacker-unknown, `api_secret_key` — the attacker never needs the secret itself, only a passively-observed valid signature/body pair). The attacker then sends this exact `raw_body`/HMAC pair directly to the app's public webhook HTTP endpoint, but with `x-shopify-shop-domain: victim.myshopify.com` and an arbitrary/randomized `x-shopify-webhook-id`. Because `HmacValidator.validate` only checks the body against the HMAC, and never checks that the given shop/webhook_id are the ones the HMAC was actually issued for, the check passes. `Registry.process` calls `handler.handle` with `WebhookMetadata` carrying the attacker-forged `shop` and `webhook_id`, while the `body` content is actually the attacker's own shop's data. A host app that follows the gem's documented pattern (`docs/usage/webhooks.md`) — trusting `data.shop` for tenant scoping and `data.webhook_id` for idempotency — will process attacker-controlled data as if it originated from the victim tenant, and will treat each randomized `webhook_id` as a new, legitimate event.

### Impact Explanation
This allows an unprivileged attacker to inject data into, or trigger tenant-scoped side effects for, an arbitrary victim shop under a webhook topic the attacker's own installation is subscribed to, and to defeat the once-only dedup guarantee host apps are told to rely on. This is a cross-tenant data-integrity break: one tenant's (attacker's) webhook payload is processed as belonging to a different tenant (victim's) namespace. It is repeatable indefinitely (new `webhook_id` per request) against any victim shop domain the attacker chooses, since the shop domain is a free-form value not tied to any real installation check in this code path.

### Likelihood Explanation
Preconditions are modest and match the permitted attacker capabilities: create a development shop, install the target app, and receive at least one real (body, HMAC) pair from a genuine webhook delivery. No secrets, tokens, or privileged access are required — the HMAC/body pair is replayed verbatim; only unsigned headers are altered. The app must expose its webhook endpoint publicly (standard for HTTP webhook delivery) and must not perform out-of-band shop/idempotency checks beyond what this gem provides — which matches the documented recommended usage.

### Recommendation
Bind the shop domain, webhook id, and topic to the authenticated signal before trusting them: e.g., require registering a per-shop (or shop-scoped) callback path/token, or validate `request.shop` against a known-installed-shop store before dispatch, and/or extend the signable string / require an out-of-band correlation the attacker cannot forge. At minimum, document (and ideally enforce in the gem) that `shop` and `webhook_id` headers are unauthenticated by HMAC and must not be used alone for tenant scoping or dedup without an independent installed-shop check.

### Proof of Concept
```ruby
# test/webhooks/registry_test.rb (illustrative addition)
def test_process_allows_shop_and_webhook_id_spoofing_with_valid_body_hmac
  received_shop = nil
  received_ids = []

  handler = TestHelpers::FakeWebhookHandler.new(
    lambda do |data|
      received_shop = data.shop
      received_ids << data.webhook_id
    end,
  )
  ShopifyAPI::Webhooks::Registry.add_registration(
    topic: @topic, path: "path", delivery_method: :http, handler: handler,
  )

  raw_body = "{\"order_id\":123}"
  hmac_digest = OpenSSL::HMAC.digest(
    OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body,
  )
  valid_hmac_header = Base64.encode64(hmac_digest)

  # Same raw_body/hmac replayed twice with attacker-chosen shop + webhook_id
  ["fake-id-1", "fake-id-2"].each do |wid|
    headers = {
      "x-shopify-topic" => @topic,
      "x-shopify-hmac-sha256" => valid_hmac_header,
      "x-shopify-shop-domain" => "victim.myshopify.com",
      "x-shopify-webhook-id" => wid,
      "x-shopify-api-version" => "2024-01",
    }
    request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
    ShopifyAPI::Webhooks::Registry.process(request)
  end

  assert_equal("victim.myshopify.com", received_shop)
  assert_equal(["fake-id-1", "fake-id-2"], received_ids)
end
```
This demonstrates that a single valid `(raw_body, hmac)` pair is accepted by `Registry.process` for arbitrarily many distinct `shop`/`webhook_id` header combinations, confirming the equality `HMAC-verified(raw_body) == (shop, webhook_id acted on)` does not hold.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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
