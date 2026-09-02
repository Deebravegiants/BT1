## Title
Webhook `shop` (and `topic`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body. The `shop-domain` and `topic` headers — which are handed to the host application's handler as the authoritative identity of the webhook — are never included in the signed payload. Any party who can obtain one validly-signed webhook body (trivially achievable by installing the app on a shop they control) can replay that exact body against the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header, and the HMAC check will still pass.

### Finding Description
`Webhooks::Registry.process` verifies authenticity with: [1](#0-0) 

The HMAC is computed only over `to_signable_string`, which returns the raw body and nothing else: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from attacker-controllable HTTP headers, independent of the signed body: [3](#0-2) 

The HMAC validator itself confirms this — it only ever hashes `verifiable_query.to_signable_string`: [4](#0-3) 

The equality this breaks: `shop authenticated by HMAC == shop delivered to the handler`. In reality, `request.shop` (and `request.topic`) are asserted, unauthenticated header values, while only `request.parsed_body` bytes are covered by the signature. `Registry.process` forwards this unauthenticated `shop` value directly to the handler: [1](#0-0) 

Because the HMAC secret (`Context.api_secret_key`, i.e. the app's `client_secret`) is shared across *every* shop that installs the app, a webhook body legitimately signed for the attacker's own shop remains validly signed no matter which `shop-domain` header accompanies it. An unprivileged attacker who installs the app on a shop they control (a normal, unprivileged action requiring no special access to any other merchant) can:
1. Trigger a real webhook (e.g. `orders/create`) on their own shop and capture the signed raw body plus HMAC.
2. Replay that same body/HMAC pair to the app's webhook endpoint with `x-shopify-shop-domain` rewritten to the victim shop's domain (and optionally forge/keep `x-shopify-topic`).
3. `HmacValidator.validate` succeeds because it only checks the body bytes, and `Registry.process` calls the handler with `shop: <victim-domain>` and the attacker's own JSON body content.

Any host application that trusts `WebhookMetadata#shop` (as the library's own documentation instructs — see `docs/usage/webhooks.md`) to key its per-tenant data writes will process attacker-supplied body content under the identity of a shop the attacker does not control — a cross-tenant data-integrity / confusion vulnerability rooted entirely in this gem's `Request`/`Registry` design, not misuse by the host app.

### Impact Explanation
This meets the Critical bar of cross-tenant access: an attacker can cause data purportedly originating "from" a merchant shop they do not own/administer to be accepted and processed by the app as authentic, using only an app installation on their own store (no leaked credentials, no privileged account, no `api_secret_key` access needed).

### Likelihood Explanation
High. Exploitation requires only: (1) installing the target app on an attacker-controlled development/trial store — which is normal, unprivileged, self-service Shopify behavior — to obtain one legitimately HMAC-signed webhook body/signature pair, and (2) POSTing that same body/signature to the app's public webhook endpoint with a forged `shop-domain` header. No secret material or privileged access to the victim's shop is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`) values into the signed material, or independently authenticate them: e.g. require the caller to supply the expected shop and compare it against a value derived from a per-shop secret/session lookup rather than trusting the unauthenticated header, or include the shop domain in the HMAC computation (mirroring how Shopify's other webhook consumers cross-check the resolved shop against their own installed-shop registry before trusting `shop-domain`). At minimum, document prominently that `Request#shop`/`#topic` are unauthenticated and must be revalidated by the host app against known installed shops before use.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the target app there.
# Shopify sends a legitimately-signed webhook to the app for that shop:
raw_body = '{"id":1,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_CLIENT_SECRET, raw_body)

# Attacker captures this valid (raw_body, hmac) pair, then replays it with a forged
# shop-domain header pointing at a victim shop the attacker does not control:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is checked),
#    handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: {...}))
#    is invoked as if Shopify itself vouched for "victim-shop.myshopify.com".
``` [5](#0-4)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
