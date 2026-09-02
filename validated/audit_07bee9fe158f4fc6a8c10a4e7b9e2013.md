### Title
Webhook `topic`, `api-version`, and `shop-domain` headers are trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so the HMAC computed by `Utils::HmacValidator.validate` only authenticates the raw body bytes, not the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers. Yet `Registry.process` uses `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` — all read straight from unauthenticated headers — to route the webhook and populate `WebhookMetadata` passed to the host app's handler [2](#0-1) . This mirrors the PoolTogether bug class: a field (`shop`) that is *acted on* (used as the tenant identity for routing/attribution) is not covered by the integrity check (`HMAC`) that is supposed to bind the payload to its origin.

### Finding Description
The identity binding that should hold is:
`hmac_valid(raw_body) == shop_domain_header_trusted_for(raw_body)`

But the code only proves:
`HMAC_secret(raw_body) == received_hmac`

It never proves that `shop-domain` (or `topic`/`webhook-id`) is the value Shopify actually associated with that specific `raw_body` when it computed the HMAC. Since Shopify webhook HMACs are computed with the app's single `client_secret`/`api_secret_key` — the same secret is valid for every shop that has installed the app — a valid `(raw_body, hmac)` pair from one tenant's webhook remains a valid pair regardless of which `shopify-shop-domain` header accompanies it.

`HmacValidator.validate` confirms only that `computed_signature(raw_body) == received_signature` [3](#0-2) , and `Request#to_signable_string` never includes the shop/topic/version/id header values in that signable string [1](#0-0) . `Registry.process` then trusts `request.shop` unconditionally to build `WebhookMetadata` for the handler [4](#0-3) .

### Impact Explanation
An attacker who controls (or is) a shop that has installed the multi-tenant app receives an authentic webhook delivery for their own shop, containing a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared `client_secret`. Because the signature covers only `raw_body`, the attacker can resend this exact body to the app's webhook endpoint while substituting `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) with an arbitrary victim shop's domain. `HmacValidator.validate` still returns `true` (the body/HMAC pair is legitimate), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop. Any host application that persists or acts on webhook data keyed by `WebhookMetadata#shop` (the documented, expected use of this API) will attribute/merge attacker-controlled data into another tenant's records — a cross-tenant data integrity violation reachable by any unprivileged app-installing user, without needing the victim's or the app's credentials.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the app on any shop (any Shopify merchant can do this for public apps) to legitimately receive one webhook with a valid HMAC, then replay it with a forged shop header to the app's public webhook endpoint. No access token, `client_secret`, or victim credentials are needed — only interception of the gem's documented behavior of trusting `request.shop`/`request.topic` for routing, which is exactly how `docs/usage/webhooks.md` and `Registry.process` are designed to be used.

### Recommendation
Ensure that any header value acted upon for tenant/topic identity is bound to the same signature verification as the body — e.g. include `shop-domain`, `topic`, and `webhook-id` in the signable string, or validate the `shop-domain` header against a value obtained through an independently authenticated channel (e.g., cross-check against a previously stored session/shop record before trusting `WebhookMetadata#shop`) before dispatching to handlers.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker.myshopify.com"
#    and receives a legitimate webhook delivery:
raw_body = '{"id":123,"note":"legit data"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_client_secret, raw_body)
headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => Base64.encode64(hmac),
  "shopify-shop-domain" => "attacker.myshopify.com",
}

# 2. Attacker replays the SAME raw_body/hmac pair but swaps the shop-domain header
forged_headers = headers.merge("shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. HMAC validation still succeeds because to_signable_string only checks raw_body:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Registry.process dispatches to the handler claiming this belongs to "victim-shop.myshopify.com"
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"id"=>123,...}, ...))
```

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
