## Title
Webhook HMAC Only Signs the Request Body, Not the `shop-domain` Header — Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body, while the `shop` (and `topic`/`webhook_id`) values that are handed to the app's handler come from HTTP headers that are never included in the signed material. This breaks the identity binding `shop attributed to webhook == shop that produced the signed body`, letting anyone who can obtain one validly-signed webhook body/HMAC pair (e.g. by installing the app on their own store) replay it with a forged `x-shopify-shop-domain` header to make the app process attacker-supplied data under a victim shop's identity.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

and `#shop` is read straight from an HTTP header with no cryptographic binding to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes and compares the signature only over `verifiable_query.to_signable_string`, i.e. only the body: [3](#0-2) 

`Registry.process` checks this HMAC and, once it passes, forwards `request.shop` (and `request.topic`, `request.webhook_id`) — none of which are covered by the HMAC — directly into `WebhookMetadata` given to the app's handler: [4](#0-3) 

The gem's own documentation asserts that `Registry.process` "will verify the request did indeed come from Shopify," implying full authenticity of the delivered metadata, not just the body bytes: [5](#0-4) 

Because the shared secret (`Context.api_secret_key`) is identical for every shop that installs the app, and the HMAC only signs the body, a merchant who installs the app on their **own** shop receives legitimately-signed webhooks (body + valid HMAC) from Shopify. That merchant can then resend the exact same body/HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body against the shared secret), and `Registry.process` will invoke the handler believing the payload originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding bypass: `shop authenticated ("dest" of trust) != shop that produced the signed bytes`. Depending on how the host application persists/acts on webhook data keyed by `data.shop` (e.g. updating records, revoking access, writing metafields, billing actions), an attacker-controlled shop can inject data attributed to an arbitrary victim shop domain, since the app has no way to distinguish this from a legitimate webhook once the body HMAC passes. This matches the Critical "cross-tenant access" impact category — data belonging to/attributed to one tenant can be forged by another tenant without needing the victim's credentials, access token, or `client_secret`.

### Likelihood Explanation
Likelihood is realistic but requires a precondition: the attacker must be a legitimate merchant who has installed the app on their own store (an "unprivileged internet user" relative to any other tenant, but not entirely anonymous — they need one shop-install of the app, which for public apps is trivial to obtain for free). Once they have any real webhook delivery, replaying it with a modified `shop-domain` header is a single crafted HTTP request to the app's public webhook endpoint; no secret, token, or additional access is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified material, or independently cross-check `request.shop` against the shop id/domain known to be associated with the specific webhook subscription (e.g., validate that a session/store record exists for that shop and that the webhook_id was actually registered for it). At minimum, document prominently that `HmacValidator`/`Registry.process` only authenticates the body bytes and that host applications must independently verify the `shop` header against their own tenant registry before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker signs up for the target Shopify app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g. `customers/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`
   - Body: `{"id":123, ...attacker-controlled fields...}`
3. Attacker captures this request (it hits their own server/proxy or a captured request log) and resends it to the same public webhook endpoint, replacing only the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - Body and `x-shopify-hmac-sha256` unchanged.
4. `HmacValidator.validate` recomputes the HMAC over the unchanged body using the shared `api_secret_key` and it matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) proceeds and calls the handler with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com`, even though the payload content actually originated from the attacker's own shop. [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
