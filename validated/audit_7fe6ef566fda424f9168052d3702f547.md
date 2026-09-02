## Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook delivery solely by HMAC-verifying the raw request body, but the tenant-identifying `shop` header (along with `topic`, `api_version`, `webhook_id`) is read from unauthenticated HTTP headers and passed straight through to the application's webhook handler. This breaks the identity binding `hmac-authenticated body == shop the body is attributed to`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop` (and `topic`, `webhook_id`, `api_version`) are pulled from HTTP headers that are never fed into the signable string: [2](#0-1) 

`Registry.process` validates the HMAC against this body-only signable string and then, without any further binding check, forwards `request.shop` to the handler as the tenant identity for the payload: [3](#0-2) 

`Utils::HmacValidator.validate` confirms this: it only ever compares against `verifiable_query.to_signable_string`, i.e., the body, never the headers: [4](#0-3) 

Because the app's `api_secret_key` is shared across all shops that install the app (it is not per-shop), any merchant who has installed the app can legitimately receive a body+HMAC pair that is valid for the shared secret (e.g., by registering their own webhook endpoint URL, or intercepting the delivery to a self-controlled callback). That attacker can then replay the exact same raw body and HMAC to the victim application's real webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header. `Registry.process` will accept it as valid — the HMAC check passes because the body is untouched — and hand the handler a `WebhookMetadata` claiming the payload belongs to an arbitrary victim shop of the attacker's choosing: [5](#0-4) 

This is the equality that should hold but does not: `shop that authorized/produced the HMAC-signed body == shop attributed to the body by Registry.process`. Since `shop` is sourced from an unauthenticated header rather than being bound into the signed content, a malicious tenant can inject content that the host application will process as though it originated from a different, victim tenant — a cross-tenant identity confusion rooted entirely in this gem's webhook verification logic.

### Impact Explanation
This allows a cross-tenant attack: an attacker who is a legitimate (even trial) merchant of the app can forge webhook deliveries that the gem will authenticate and attribute to a shop they do not control, corrupting or injecting data into another merchant's tenant state via the app's webhook handlers. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is Low/Medium: it requires the attacker to install the target app on a shop they control (readily available for any app with a public listing or dev store) and to be able to route/replay the resulting webhook body to the target's public webhook endpoint with a modified shop header — both are within the capability of an unprivileged internet user with no special credentials, since no access token, `api_secret_key`, or victim account access is needed.

### Recommendation
Bind the tenant-identifying and routing-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) into the HMAC-signed content, or otherwise cryptographically bind them to the body (e.g., verify against a per-installation expected shop as supplied by the caller) before `Registry.process` forwards them to handlers, so that no header value used for tenant attribution or handler dispatch can be altered independently of the HMAC-covered payload.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and configures/observes the webhook delivery URL and payload (or points delivery to a callback they control), capturing a raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (valid because the secret is shared per-app, not per-shop).
2. Attacker sends `POST <app's real webhook endpoint>` with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - `X-Shopify-Topic: <chosen topic>` (optionally changed)
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `B` against `H`: [6](#0-5) 
4. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B`, causing the app to process/store attacker data as belonging to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
