### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) Metadata Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw request body only, while the tenant-identifying `shop` header (along with `topic`, `webhook_id`, `api_version`) is read directly from unauthenticated HTTP headers and handed to the app's webhook handler as trusted metadata. Because the HMAC signature never covers these headers, an attacker who possesses one legitimately signed `(body, hmac)` pair can replay it against the app's public webhook endpoint while swapping the `shop` header to an arbitrary victim tenant, and the signature check still passes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are parsed straight from HTTP headers, with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate_signature` verifies the HMAC strictly against `to_signable_string` (i.e., the body): [3](#0-2) 

`Webhooks::Registry.process` trusts `Utils::HmacValidator.validate(request)` as the sole authentication check, then forwards the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` straight into the `WebhookMetadata` object passed to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop header == shop cryptographically bound to signed bytes`. In this implementation the equality actually enforced is only `hmac(body) == received_hmac`; the `shop` header is completely outside that verified byte range. This is the same class of defect as the referenced report's `extendTime()` issue — a value that gates a security-relevant decision (there: refund eligibility window; here: which tenant a webhook payload is attributed to) is controlled independently of the value that is actually integrity-checked.

### Impact Explanation
Any app built on this library that keys per-tenant behavior off `WebhookMetadata#shop` (the documented/intended way to determine which merchant a webhook applies to) can be made to process a valid, HMAC-passing webhook body under an arbitrary victim shop identity. An attacker who legitimately owns one Shopify store (e.g., a free development store, obtainable without any privileged relationship to the target) can capture one authentic `(body, X-Shopify-Hmac-Sha256)` pair generated for their own store, then submit it directly to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to the victim's shop. `Utils::HmacValidator.validate` still returns `true` because it never inspects the header. This is a cross-tenant identity binding bypass, matching the "Critical: cross-tenant access" impact category.

### Likelihood Explanation
The webhook endpoint is inherently public (it must be reachable by Shopify's infrastructure without prior authentication, relying solely on HMAC for trust). Obtaining a legitimate `(body, hmac)` pair requires nothing more than operating one's own Shopify store/app installation — no access to `api_secret_key`, no privileged account, and no interaction with the victim tenant. The only additional step is a direct HTTP POST with a modified header, which is trivial for any unprivileged internet user with basic tooling (e.g., `curl`).

### Recommendation
Include the tenant-identifying headers (`shop`, and ideally `topic`/`webhook_id`) in the signed payload used for HMAC verification, or otherwise cryptographically bind them to the body (e.g., verify that `shop` matches a value embedded in the JSON body, or require the host application to independently confirm delivery legitimacy using Shopify's webhook subscription records for that shop/topic/id combination) before trusting `WebhookMetadata#shop` for tenant routing.

### Proof of Concept
```
# 1. Attacker owns "attacker-shop.myshopify.com" and receives a real,
#    Shopify-signed webhook for their own store:
POST /webhooks HTTP/1.1
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <valid HMAC of BODY using the app's real secret>
X-Shopify-Shop-Domain: attacker-shop.myshopify.com
X-Shopify-Webhook-Id: aaaa-...

BODY

# 2. Attacker replays the identical BODY and X-Shopify-Hmac-Sha256,
#    but substitutes the shop header:
POST /webhooks HTTP/1.1
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <same valid HMAC, unchanged>
X-Shopify-Shop-Domain: victim-shop.myshopify.com
X-Shopify-Webhook-Id: aaaa-...

BODY

# ShopifyAPI::Webhooks::Registry.process still succeeds because
# Utils::HmacValidator.validate only checks HMAC(BODY); the handler
# receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
# and processes attacker-controlled data under the victim's identity.
``` [4](#0-3)

### Citations

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
